# Generated by Django 4.2.7 on 2023-12-30 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avocat', '0004_alter_avocat_evaluationstar'),
    ]

    operations = [
        migrations.AddField(
            model_name='avocat',
            name='photo',
            field=models.ImageField(blank=True, default='avatar.jpg', null=True, upload_to=''),
        ),
    ]