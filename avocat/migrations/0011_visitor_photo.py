# Generated by Django 4.2.7 on 2023-12-31 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avocat', '0010_alter_visitor_lastname'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='photo',
            field=models.ImageField(blank=True, default='visitor.png', null=True, upload_to=''),
        ),
    ]