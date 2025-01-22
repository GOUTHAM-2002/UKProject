# Generated by Django 5.1.4 on 2025-01-21 12:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('therapist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pings', to='user_management.therapist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pinged_therapists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('therapist', 'user')},
            },
        ),
    ]
