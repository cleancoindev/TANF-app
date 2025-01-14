"""Utility file for functions shared between all parsers even preparser."""


def value_is_empty(value, length):
    """Handle 'empty' values as field inputs."""
    empty_values = [
        ' '*length,  # '     '
        '#'*length,  # '#####'
    ]

    return value is None or value in empty_values


class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, name, type, startIndex, endIndex, required=True, validators=[]):
        self.name = name
        self.type = type
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.required = required
        self.validators = validators

    def create(self, name, length, start, end, type):
        """Create a new field."""
        return Field(name, type, length, start, end)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.startIndex}-{self.endIndex})"

    def parse_value(self, line):
        """Parse the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]

        if value_is_empty(value, self.endIndex-self.startIndex):
            return None

        match self.type:
            case 'number':
                try:
                    value = int(value)
                    return value
                except ValueError:
                    return None
            case 'string':
                return value


class RowSchema:
    """Maps the schema for data lines."""

    def __init__(
            self,
            model=dict,
            preparsing_validators=[],
            postparsing_validators=[],
            fields=[],
            quiet_preparser_errors=False
            ):
        self.model = model
        self.preparsing_validators = preparsing_validators
        self.postparsing_validators = postparsing_validators
        self.fields = fields
        self.quiet_preparser_errors = quiet_preparser_errors

    def _add_field(self, name, length, start, end, type):
        """Add a field to the schema."""
        self.fields.append(
            Field(name, type, start, end)
        )

    def add_fields(self, fields: list):
        """Add multiple fields to the schema."""
        for field, length, start, end, type in fields:
            self._add_field(field, length, start, end, type)

    def get_all_fields(self):
        """Get all fields from the schema."""
        return self.fields

    def parse_and_validate(self, line):
        """Run all validation steps in order, and parse the given line into a record."""
        errors = []

        # run preparsing validators
        preparsing_is_valid, preparsing_errors = self.run_preparsing_validators(line)

        if not preparsing_is_valid:
            if self.quiet_preparser_errors:
                return None, True, []
            return None, False, preparsing_errors

        # parse line to model
        record = self.parse_line(line)

        # run field validators
        fields_are_valid, field_errors = self.run_field_validators(record)

        # run postparsing validators
        postparsing_is_valid, postparsing_errors = self.run_postparsing_validators(record)

        is_valid = fields_are_valid and postparsing_is_valid
        errors = field_errors + postparsing_errors

        return record, is_valid, errors

    def run_preparsing_validators(self, line):
        """Run each of the `preparsing_validator` functions in the schema against the un-parsed line."""
        is_valid = True
        errors = []

        for validator in self.preparsing_validators:
            validator_is_valid, validator_error = validator(line)
            is_valid = False if not validator_is_valid else is_valid
            if validator_error:
                errors.append(validator_error)

        return is_valid, errors

    def parse_line(self, line):
        """Create a model for the line based on the schema."""
        record = self.model()

        for field in self.fields:
            value = field.parse_value(line)

            if value is not None:
                if isinstance(record, dict):
                    record[field.name] = value
                else:
                    setattr(record, field.name, value)

        return record

    def run_field_validators(self, instance):
        """Run all validators for each field in the parsed model."""
        is_valid = True
        errors = []

        for field in self.fields:
            for validator in field.validators:
                value = None
                if isinstance(instance, dict):
                    value = instance.get(field.name, None)
                else:
                    value = getattr(instance, field.name, None)

                if field.required and not value_is_empty(value, field.endIndex-field.startIndex):
                    validator_is_valid, validator_error = validator(value)
                    is_valid = False if not validator_is_valid else is_valid
                    if validator_error:
                        errors.append(validator_error)
                elif field.required:
                    is_valid = False
                    errors.append(f"{field.name} is required but a value was not provided.")

        return is_valid, errors

    def run_postparsing_validators(self, instance):
        """Run each of the `postparsing_validator` functions against the parsed model."""
        is_valid = True
        errors = []

        for validator in self.postparsing_validators:
            validator_is_valid, validator_error = validator(instance)
            is_valid = False if not validator_is_valid else is_valid
            if validator_error:
                errors.append(validator_error)

        return is_valid, errors


class MultiRecordRowSchema:
    """Maps a line to multiple `RowSchema`s and runs all parsers and validators."""

    def __init__(self, schemas):
        # self.common_fields = None
        self.schemas = schemas

    def parse_and_validate(self, line):
        """Run `parse_and_validate` for each schema provided and bubble up errors."""
        records = []

        for schema in self.schemas:
            r = schema.parse_and_validate(line)
            records.append(r)

        return records
