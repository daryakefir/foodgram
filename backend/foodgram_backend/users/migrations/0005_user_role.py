# Generated by Django 3.2.3 on 2024-09-30 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_remove_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('admin', 'Admin')], default='user', max_length=5, verbose_name='Права пользователя'),
        ),
    ]
