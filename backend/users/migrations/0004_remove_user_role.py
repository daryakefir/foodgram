# Generated by Django 3.2.3 on 2024-09-30 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
