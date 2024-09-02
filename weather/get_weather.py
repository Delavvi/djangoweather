import requests
import pycountry
from django.core.mail import send_mail
from django.template.loader import render_to_string
from weather.serializers import WeatherSerializer
from django.conf import settings
from celery import shared_task


class WrongSpelling(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f'{self.message}'


@shared_task
def send_weather_email(emails: list, data: list):
    message = render_to_string('weather_email.html', {
        'data': data
    })
    mail_subject = f'Weather forecast'
    send_mail(mail_subject, message, recipient_list=emails, html_message=message, from_email=settings.EMAIL_HOST_USER)


def country_name_to_code(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2, country.alpha_3
    except LookupError:
        raise WrongSpelling("Country does not exist")


def fetch_weather(city: str, country: str):
    api_key = settings.API_KEY
    code = country_name_to_code(country)
    response = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city},{code}&appid={api_key}').json()
    if not response:
        raise WrongSpelling("City does not exist")
    lat, long = response[0]['lat'], response[0]['lon']
    forcast_response = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={api_key}').json()
    weather = {
        'name': city,
        'country': country,
        'temperature': round(forcast_response['main']['temp'] - 273.15, 2),
        'description': forcast_response['weather'][0]['description'],
        'icon': forcast_response['weather'][0]['icon']
    }
    return weather


def update_weather_instance(object_to_update):
    api_key = settings.API_KEY
    response = fetch_weather(object_to_update.city.name, object_to_update.city.country)
    response['city'] = object_to_update.city.pk
    serialized = WeatherSerializer(data=response, instance=object_to_update)
    serialized.is_valid(raise_exception=True)
    updated_data = serialized.save()
    return updated_data
