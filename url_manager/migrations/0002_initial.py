# Generated by Django 4.2.20 on 2025-04-14 04:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("url_manager", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="urlitem",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="url_items",
                to=settings.AUTH_USER_MODEL,
                verbose_name="ユーザー",
            ),
        ),
    ]
