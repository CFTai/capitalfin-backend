# Generated by Django 5.0.6 on 2024-06-25 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("invest", "0004_alter_invest_invest_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="invest",
            options={"ordering": ["id"]},
        ),
        migrations.AlterModelOptions(
            name="investbonustransaction",
            options={"ordering": ["id"]},
        ),
    ]