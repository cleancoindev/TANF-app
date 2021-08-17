# Generated by Django 3.2.5 on 2021-08-16 14:10
from django.db import migrations

from tdpservice.users.permissions import (
    delete_permissions_q,
    get_permission_ids_for_model,
    view_permissions_q
)


def set_ofa_admin_permissions(apps, schema_editor):
    """Set relevant Group Permissions for OFA Admin group."""
    ofa_admin = apps.get_model('auth', 'Group').objects.get(name='OFA Admin')

    # For the User model OFA Admin will have all permissions *except* delete
    user_permissions = get_permission_ids_for_model(
        'users',
        'user',
        exclusions=[delete_permissions_q]
    )

    # The rest of the permissions are view only
    region_permissions = get_permission_ids_for_model(
        'stts',
        'region',
        filters=[view_permissions_q]
    )
    stt_permissions = get_permission_ids_for_model(
        'stts',
        'stt',
        filters=[view_permissions_q]
    )
    datafile_permissions = get_permission_ids_for_model(
        'data_files',
        'datafile',
        filters=[view_permissions_q]
    )
    logentry_permissions = get_permission_ids_for_model(
        'admin',
        'logentry',
        filters=[view_permissions_q]
    )

    # Clear existing permissions that may be set so we can ensure pristine state
    ofa_admin.permissions.clear()

    # Assign correct permissions
    ofa_admin.permissions.add(*user_permissions)
    ofa_admin.permissions.add(*region_permissions)
    ofa_admin.permissions.add(*stt_permissions)
    ofa_admin.permissions.add(*datafile_permissions)
    ofa_admin.permissions.add(*logentry_permissions)


def unset_ofa_admin_permissions(apps, schema_editor):
    """Remove all Group Permissions added to OFA Admin."""
    ofa_admin = apps.get_model('auth', 'Group').objects.get(name='OFA Admin')
    ofa_admin.permissions.clear()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('users', '0017_unset_superuser_flag'),
    ]

    operations = [
        migrations.RunPython(
            set_ofa_admin_permissions,
            reverse_code=unset_ofa_admin_permissions
        )
    ]
