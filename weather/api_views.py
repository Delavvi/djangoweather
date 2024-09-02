from datetime import timedelta
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Cities, WeatherData, Subscription
from .get_weather import fetch_weather, WrongSpelling, update_weather_instance
from .serializers import WeatherSerializer, CitySerializer, SubscriptionSerializer, UserSerializer
from django.utils import timezone
from .get_weather import send_weather_email
from .permission import IsAuthenticated
from rest_framework.permissions import AllowAny
from .tasks import send_emails


class DefaultWeather(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city, country):
        self.city = city
        self.country = country
        response = self.get_queryset()
        if response:
            serialized = WeatherSerializer(response)
            response = json.dumps(serialized.data)
            return Response(response)
        else:
            try:
                response = fetch_weather(city, country)
            except WrongSpelling:
                return Response({'error': 'country name or city name was misspelled'}, 400)
            city_serializer = CitySerializer(data=response)
            city_serializer.is_valid(raise_exception=True)
            city_instance = city_serializer.save()
            data = response.copy()
            data['city'] = city_instance.pk
            weather_serializer = WeatherSerializer(data=data)
            weather_serializer.is_valid(raise_exception=True)
            weather_serializer.save()
            return Response(weather_serializer.data)

    def get_queryset(self):
        city = getattr(self, 'city', None)
        country = getattr(self, 'country', None)
        response = Cities.objects.filter(name=city, country=country).first()
        if not response:
            return WeatherData.objects.none()
        weather_data = WeatherData.objects.filter(city=response).first()
        if not weather_data:
            return WeatherData.objects.none()
        if timezone.now() - weather_data.created_at > timedelta(
                hours=0) or timezone.now() - weather_data.updated_at > timedelta(hours=1):
            weather_data = update_weather_instance(weather_data)
        return weather_data


class SubscriptionChecker(RetrieveAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_pk = self.request.user.pk
        city_pk = self.kwargs.get('pk')
        return Subscription.objects.filter(users=user_pk, cities=city_pk)


class CreateDeleteUpdateGetSubscriptionView(CreateModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()

    def post(self, request, *args, **kwargs):
        created = self.create(request, *args, **kwargs)
        city_pk = request.data.get('cities')[0]
        try:
            city = Cities.objects.get(pk=city_pk)
        except Cities.DoesNotExist:
            return Response({"detail": "City not found."}, status=status.HTTP_404_NOT_FOUND)
        data = {'city': city.name, 'country': city.country, 'description': city.city.description,
                'icon': city.city.icon, 'temperature': city.city.temperature}
        send_weather_email([request.user.email], [data])
        return created

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        subscription_id = request.data.get('subscription_id')
        new_period = int(request.data.get('new_period'))
        if new_period not in [1, 3, 6, 12]:
            return Response({'detail': 'possible notification period are 1, 3, 6, 12.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            subscribe_instance = Subscription.objects.filter(pk=subscription_id).first()
        except Subscription.DoesNotExist:
            return Response({'detail': "Subscription does not exist"}, status=status.HTTP_404_NOT_FOUND)
        subscribe_instance.notification_period = new_period
        subscribe_instance.save()
        serialized = SubscriptionSerializer(subscribe_instance)
        return Response(serialized.data, status=201)

    def get(self, request, *args, **kwargs):
        user = request.user
        subscriptions = Subscription.objects.filter(users=user).prefetch_related('cities')
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=200)


class RegisterUser(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            response_data = {'access_token': str(access_token), 'refresh_token': str(refresh)}
            return Response(response_data, 201)
        else:
            return Response({'Error': 'Provided email or name was taken'}, 400)


class Check(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        send_emails.delay()
        return Response({'resp': 'get'})
