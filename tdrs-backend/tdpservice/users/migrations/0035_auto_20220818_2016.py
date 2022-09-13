# Generated by Django 3.2.13 on 2022-08-18 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_user_account_approval_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='access_request',
            field=models.BooleanField(default=False, help_text='Deprecated: use Account Approval Status instead - Designates whether this user account has requested access to TDP. Users with this checked must have groups assigned for the application to work correctly.'),
        ),
        migrations.AlterField(
            model_name='user',
            name='deactivated',
            field=models.BooleanField(default=False, help_text='Deprecated: use Account Approval Status instead - Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='deactivated'),
        ),
    ]
