# Generated by Django 4.2.2 on 2023-07-27 13:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("goldmine", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="goldminebonussettings",
            old_name="level",
            new_name="max_level",
        ),
    ]
