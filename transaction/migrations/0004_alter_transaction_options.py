# Generated by Django 5.0.6 on 2024-06-25 13:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("transaction", "0003_alter_transaction_transaction_type"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="transaction",
            options={"ordering": ["id"]},
        ),
    ]
