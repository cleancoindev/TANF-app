# Generated by Django 3.2.10 on 2022-01-22 17:10

from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0027_user_hhs_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='access_request',
            field=models.BooleanField(default=False, help_text=_(
                'Designates whether this user account has requested access to TDP. '
                'Users with this checked must have groups assigned for the application to work correctly.'
            ), ),
        ),
    ]