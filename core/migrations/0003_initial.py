# Generated by Django 4.2.20 on 2025-04-14 04:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to=settings.AUTH_USER_MODEL,
                verbose_name="ユーザー",
            ),
        ),
    ]
