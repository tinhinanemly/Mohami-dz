# Generated by Django 4.2.7 on 2023-12-31 02:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avocat', '0007_alter_phonenumbers_coordonnees'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='created',
        ),
        migrations.AlterField(
            model_name='post',
            name='dateTimePub',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]