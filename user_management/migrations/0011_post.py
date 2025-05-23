# Generated by Django 5.1.4 on 2025-02-12 11:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0010_remove_chatmessage_ping_remove_message_is_read_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('post_type', models.CharField(choices=[('image', 'Image'), ('video', 'Video'), ('article', 'Article')], max_length=7)),
                ('media_file', models.FileField(blank=True, null=True, upload_to='posts/')),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='post_thumbnails/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('upvote_count', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='user_management.therapist')),
                ('upvotes', models.ManyToManyField(blank=True, related_name='upvoted_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
