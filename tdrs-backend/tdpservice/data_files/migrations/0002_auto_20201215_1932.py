# Generated by Django 3.1.1 on 2020-12-15 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reportfile",
            name="slug",
            field=models.CharField(max_length=256),
        ),
    ]
