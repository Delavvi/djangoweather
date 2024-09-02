from django.core.management.base import BaseCommand
from ...models import MyUser, Cities, Subscription, WeatherData
from djangoweather.settings.prod import TEST_EMAIL, SECOND_TEST_EMAIL


class Command(BaseCommand):
    help = 'Fill database with fake data'

    def handle(self, *args, **options):
        user = MyUser.objects.create_user(username='tester', password='test', email=TEST_EMAIL)
        s_user = MyUser.objects.create_user(username='stester', password='stest', email=SECOND_TEST_EMAIL)
        city = Cities.objects.create(name='Berlin', country='Germany')
        second_city = Cities.objects.create(name='Madrid', country='Spain')
        subscription = Subscription.objects.create(notification_period=1)
        second_subscription = Subscription.objects.create(notification_period=1)
        third_subscription = Subscription.objects.create(notification_period=1)
        subscription.users.add(user)
        subscription.cities.add(city)
        third_subscription.users.add(s_user)
        third_subscription.cities.add(city)
        second_subscription.cities.add(second_city)
        second_subscription.users.add(user)
        city_weather = WeatherData.objects.create(description='nice', temperature=10, icon='1od', city=city)
        second_city_weather = WeatherData.objects.create(description='OK', temperature=40, icon='1od', city=second_city)
