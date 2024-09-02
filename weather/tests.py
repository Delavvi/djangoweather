from unittest import mock

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import MyUser, Cities, Subscription, WeatherData
from .api_views import DefaultWeather, SubscriptionChecker, CreateDeleteUpdateGetSubscriptionView, RegisterUser
from .tasks import send_emails


class TestDefaultWeather(TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.email = 'tester@gmail.com'
        self.user = MyUser.objects.create_user(username=self.username, password=self.password, email=self.email,
                                               is_active=True)
        self.factory = APIRequestFactory()
        self.request = self.factory.post("api/ver1/token/",  {'email': self.email, 'password': self.password})
        self.city = Cities.objects.create(name='Zaporizhzha', country='Ukraine')
        self.subscription = Subscription.objects.create(notification_period=1)
        self.subscription.users.add(self.user)
        self.subscription.cities.add(self.city)
        self.city_weather = WeatherData.objects.create(description='nice', temperature=10, icon='1od', city=self.city)

    def test_success_base_weather(self):
        request = self.factory.get("api/ver1/weather/")
        force_authenticate(request=request, user=self.user)
        view = DefaultWeather.as_view()
        response = view(request, city='Berlin', country='Germany')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['city'], 10)

    def test_failure_base_weather(self):
        request = self.factory.get("api/ver1/weather/")
        force_authenticate(request=request, user=self.user)
        view = DefaultWeather.as_view()
        response = view(request, city='Wron', country='Grg')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'country name or city name was misspelled')

    def test_check_subscription_failure(self):
        request = self.factory.get("api/ver1/subscription-checker/")
        view = SubscriptionChecker.as_view()
        force_authenticate(request, self.user)
        response = view(request, pk=10)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'No Subscription matches the given query.')

    def test_check_subscription_success(self):
        request = self.factory.get("api/ver1/subscription-checker/")
        view = SubscriptionChecker.as_view()
        force_authenticate(request, self.user)
        response = view(request, pk=self.city.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['notification_period'], 1)

    def test_make_subscription_success(self):
        data = {'notification_period': 1, 'cities': [self.city.pk]}
        request = self.factory.post('/api/ver1/subscription/', data, format='json')
        view = CreateDeleteUpdateGetSubscriptionView.as_view()
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['notification_period'], 1)

    def test_make_subscription_error(self):
        data = {'notification_period': 1, 'cities': [10]}
        request = self.factory.post('/api/ver1/subscription/', data, format='json')
        view = CreateDeleteUpdateGetSubscriptionView.as_view()
        force_authenticate(request, self.user)
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['cities'][0], 'Invalid pk "10" - object does not exist.')

    def test_delete_subscription_success(self):
        request = self.factory.delete('/api/ver1/subscription/')
        view = CreateDeleteUpdateGetSubscriptionView.as_view()
        force_authenticate(request, user=self.user)
        response = view(request, pk=self.subscription.pk)
        self.assertEqual(response.status_code, 204)

    def test_get_subscription(self):
        request = self.factory.get('/api/ver1/subscription/')
        view = CreateDeleteUpdateGetSubscriptionView.as_view()
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.data[0]['id'], 6)
        self.assertEqual(response.status_code, 200)

    def test_update_subscription(self):
        subscription_id = self.subscription.pk
        data = {'new_period': 12, 'subscription_id': subscription_id}
        request = self.factory.put('/api/ver1/subscription/', data)
        view = CreateDeleteUpdateGetSubscriptionView.as_view()
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['notification_period'], 12)


class TestRegister(TestCase):
    def setUp(self):
        self.username = 'Tester'
        self.password = '12DdDXCV12'
        self.email = 'jozeph1313d@gmail.com'
        self.factory = APIRequestFactory()

    def test_register(self):
        data = {'password': self.password, 'username': self.username, 'email': self.email}
        request = self.factory.post('api/ver1/register', data, format='json')
        view = RegisterUser.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['refresh_token'])
        self.assertIsNotNone(response.data['access_token'])

    def test_register_error(self):
        user = MyUser.objects.create_user(email=self.email, username=self.username, password=self.password)
        data = {'password': self.password, 'username': self.username, 'email': self.email}
        request = self.factory.post('api/ver1/register', data, format='json')
        view = RegisterUser.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['Error'], 'Provided email or name was taken')


class TestToken(TestCase):
    def setUp(self):
        self.name = 'name'
        self.email = 'emaild@gmail.com'
        self.password = '123456gh'
        self.user = MyUser.objects.create_user(username=self.name, email=self.email, password=self.password)
        self.factory = APIRequestFactory()

    def test_access_refresh_token(self):
        data = {'password': self.password, 'username': self.name, 'email': self.email}
        view = TokenObtainPairView.as_view()
        request = self.factory.post('api/ver1/token/', data, format='json')
        response = view(request)


class TestCeleryTask(TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.email = 'jozeph1313d@gmail.com'
        self.user = MyUser.objects.create_user(username=self.username, password=self.password, email=self.email,
                                               is_active=True)
        self.factory = APIRequestFactory()
        self.city = Cities.objects.create(name='Zaporizhzha', country='Ukraine')
        self.subscription = Subscription.objects.create(notification_period=1)
        self.subscription.users.add(self.user)
        self.subscription.cities.add(self.city)
        self.city_weather = WeatherData.objects.create(description='nice', temperature=10, icon='1od', city=self.city)

    def test_task(self):
        with mock.patch('weather.tasks.send_emails.apply_async') as mock_send_emails:
            send_emails.apply_async()
            mock_send_emails.assert_called_once()
