from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from weather.models import Subscription, Cities
from django.contrib.postgres.aggregates import ArrayAgg
from weather.get_weather import send_weather_email, update_weather_instance
import logging
from djangoweather.celery import app
from celery import shared_task, group, chord

twelve_hour = [8, 20]
six_hour = [8, 14, 20, 2]
three_hour = [8, 11, 14, 17, 20, 23, 2, 5]

logger = logging.getLogger(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3600.0, send_emails.s(), name='add every hour')


@shared_task
def send_emails():
    try:
        cities = get_email_query_set()
        grouped_tasks = group(tget_weather.s(city) for city in cities)
        weather_results = chord(grouped_tasks)(group_user_weather.s())
        weather = weather_results.get()
        sending_task = group(send_weather_email.s([email], weather_data) for email, weather_data in weather.items())
        sending_task.apply_async()
    except Exception as e:
        logger.error('Error in send_emails task: %s', str(e))
        raise e


@shared_task
def tsend_email(emails: list, data: list):
    message = render_to_string('weather_email.html', {
        'data': data
    })
    mail_subject = f'Weather forecast'
    send_mail(mail_subject, message, recipient_list=emails, html_message=message,
              from_email=settings.EMAIL_HOST_USER)


@shared_task
def tget_weather(city):
    logger.error(city['cities__pk'])
    logger.error(Cities.objects.all())
    city_object = Cities.objects.get(pk=city['cities__pk'])
    weather = update_weather_instance(object_to_update=city_object.city)
    city['temperature'] = weather.temperature
    city['description'] = weather.description
    city['icon'] = weather.icon
    city['city'] = city_object.name
    city['country'] = city_object.country
    return city


@shared_task
def group_user_weather(emails_grouped_by_city: dict):
    email_weather = {}
    for emails in emails_grouped_by_city:
        weather_data = {'temperature': emails['temperature'], 'description': emails['description'],
                        'icon': emails['icon'], 'city': emails['city'], 'country': emails['country']}
        for email in emails['emails']:
            if email in email_weather:
                email_weather[email].append(weather_data)
            else:
                email_weather[email] = [weather_data]
    return email_weather


def get_email_query_set():
    now = timezone.now()
    if now.hour in [8, 20]:
        subscription_query = Subscription.objects.filter(notification_period__in=[1, 3, 6, 12])
    elif now.hour in [14, 2]:
        subscription_query = Subscription.objects.filter(notification_period__in=[1, 3, 6])
    elif now.hour in [11, 17, 23, 5]:
        subscription_query = Subscription.objects.filter(notification_period__in=[1, 3])
    else:
        subscription_query = Subscription.objects.filter(notification_period=1)
    emails = get_emails(subscription_query)
    return emails


def get_emails(queryset):
    grouped_cities_emails = queryset.values('cities__pk').annotate(emails=ArrayAgg('users__email'))
    return grouped_cities_emails

