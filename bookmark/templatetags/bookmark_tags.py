from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter
def timesince_days(value):
    """日付から経過日数を返す"""
    if not value:
        return None

    now = timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value)

    delta = now.date() - value.date()
    return delta.days
