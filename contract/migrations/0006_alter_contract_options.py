# Generated by Django 5.0.6 on 2024-06-25 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("contract", "0005_alter_contract_contract_status"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="contract",
            options={"ordering": ["id"]},
        ),
    ]