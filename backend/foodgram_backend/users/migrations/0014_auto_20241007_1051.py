# Generated by Django 3.2.3 on 2024-10-07 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_follow_no_self_following'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'default_related_name': 'followers', 'ordering': ('user',)},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'default_related_name': 'users', 'ordering': ('username',)},
        ),
    ]
