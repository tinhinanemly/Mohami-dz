# Generated by Django 4.2.7 on 2023-12-27 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avocat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='avocat',
            name='experienceWork',
            field=models.DateField(null=True),
        ),
    ]
