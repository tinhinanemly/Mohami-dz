# Generated by Django 4.2.7 on 2024-01-26 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avocat', '0011_visitor_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avocat',
            name='evaluationStar',
            field=models.IntegerField(default=0, null=True),
        ),
    ]