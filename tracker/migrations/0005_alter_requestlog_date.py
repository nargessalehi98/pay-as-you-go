# Generated by Django 4.1 on 2023-08-24 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_alter_requestlog_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='date',
            field=models.DateField(),
        ),
    ]
