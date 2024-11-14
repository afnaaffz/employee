# Generated by Django 5.0.4 on 2024-11-14 17:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('new_app', '0003_meeting_delete_industryprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='RSVP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('attending', 'Attending'), ('not_attending', 'Not Attending')], max_length=50)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='new_app.meeting')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]