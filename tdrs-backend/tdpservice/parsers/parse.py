"""Convert raw uploaded Datafile into a parsed model, and accumulate/return any errors."""


import os
from . import schema_defs, validators, util
from tdpservice.data_files.models import DataFile


def parse_datafile(datafile):
    """Parse and validate Datafile header/trailer, then select appropriate schema and parse/validate all lines."""
    rawfile = datafile.file
    errors = {}

    document_is_valid, document_error = validators.validate_single_header_trailer(rawfile)
    if not document_is_valid:
        errors['document'] = [document_error]
        return errors

    # get header line
    rawfile.seek(0)
    header_line = rawfile.readline().decode().strip()

    # get trailer line
    rawfile.seek(0)
    rawfile.seek(-2, os.SEEK_END)
    while rawfile.read(1) != b'\n':
        rawfile.seek(-2, os.SEEK_CUR)

    trailer_line = rawfile.readline().decode().strip('\n')

    # parse header, trailer
    header, header_is_valid, header_errors = schema_defs.header.parse_and_validate(header_line)
    if not header_is_valid:
        errors['header'] = header_errors
        return errors

    trailer, trailer_is_valid, trailer_errors = schema_defs.trailer.parse_and_validate(trailer_line)
    if not trailer_is_valid:
        errors['trailer'] = trailer_errors

    # ensure file section matches upload section
    section_names = {
        'TAN': {
            'A': DataFile.Section.ACTIVE_CASE_DATA,
            'C': DataFile.Section.CLOSED_CASE_DATA,
            'G': DataFile.Section.AGGREGATE_DATA,
            'S': DataFile.Section.STRATUM_DATA,
        },
        'SSP': {
            'A': DataFile.Section.SSP_ACTIVE_CASE_DATA,
            'C': DataFile.Section.SSP_CLOSED_CASE_DATA,
            'G': DataFile.Section.SSP_AGGREGATE_DATA,
            'S': DataFile.Section.SSP_STRATUM_DATA,
        },
    }

    program_type = header['program_type']
    section = header['type']

    if datafile.section != section_names.get(program_type, {}).get(section):
        errors['document'] = ['Section does not match.']
        return errors

    line_errors = parse_datafile_lines(datafile, program_type, section)

    errors = errors | line_errors

    return errors


def parse_datafile_lines(datafile, program_type, section):
    """Parse lines with appropriate schema and return errors."""
    errors = {}
    rawfile = datafile.file

    rawfile.seek(0)
    line_number = 0
    schema_options = get_schema_options(program_type)

    for rawline in rawfile:
        line_number += 1
        line = rawline.decode().strip('\r\n')

        if line.startswith('HEADER') or line.startswith('TRAILER'):
            continue

        schema = get_schema(line, section, schema_options)

        if isinstance(schema, util.MultiRecordRowSchema):
            records = parse_multi_record_line(line, schema)

            record_number = 0
            for r in records:
                record_number += 1
                record, record_is_valid, record_errors = r
                if not record_is_valid:
                    line_errors = errors.get(line_number, {})
                    line_errors[record_number] = record_errors
                    errors[line_number] = line_errors
        else:
            record_is_valid, record_errors = parse_datafile_line(line, schema)
            if not record_is_valid:
                errors[line_number] = record_errors

    return errors


def parse_multi_record_line(line, schema):
    """Parse and validate a datafile line using MultiRecordRowSchema."""
    if schema:
        records = schema.parse_and_validate(line)

        for r in records:
            record, record_is_valid, record_errors = r

            if record:
                record.save()

        return records

    return [(None, False, ['No schema selected.'])]


def parse_datafile_line(line, schema):
    """Parse and validate a datafile line and save any errors to the model."""
    if schema:
        record, record_is_valid, record_errors = schema.parse_and_validate(line)

        if record:
            record.save()

        return record_is_valid, record_errors

    return (False, ['No schema selected.'])


def get_schema_options(program_type):
    """Return the allowed schema options."""
    match program_type:
        case 'TAN':
            return {
                'A': {
                    'T1': schema_defs.tanf.t1,
                    'T2': schema_defs.tanf.t2,
                    'T3': schema_defs.tanf.t3,
                },
                'C': {
                    # 'T4': schema_options.t4,
                    # 'T5': schema_options.t5,
                },
                'G': {
                    # 'T6': schema_options.t6,
                },
                'S': {
                    # 'T7': schema_options.t7,
                },
            }
        case 'SSP':
            return {
                'A': {
                    'M1': schema_defs.ssp.m1,
                    'M2': schema_defs.ssp.m2,
                    'M3': schema_defs.ssp.m3,
                },
                'C': {
                    # 'M4': schema_options.m4,
                    # 'M5': schema_options.m5,
                },
                'G': {
                    # 'M6': schema_options.m6,
                },
                'S': {
                    # 'M7': schema_options.m7,
                },
            }
        # case tribal?
    return None


def get_schema(line, section, schema_options):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return schema_options.get(section, {}).get(line_type, None)
