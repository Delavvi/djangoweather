from django.utils import timezone
from rest_framework import serializers
from .models import WeatherData, Cities, Subscription, MyUser
from django.contrib.auth.hashers import make_password


class WeatherSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    description = serializers.CharField(max_length=30)
    icon = serializers.CharField(max_length=30)
    city = serializers.PrimaryKeyRelatedField(queryset=Cities.objects.all())

    def create(self, validated_data):
        weather_object = WeatherData.objects.create(
            icon=validated_data['icon'],
            temperature=validated_data['temperature'],
            description=validated_data['description'],
            city=validated_data['city']
        )
        return weather_object

    def update(self, instance, validated_data):
        instance.icon = validated_data.get('icon', instance.icon)
        instance.temperature = validated_data.get('temperature', instance.temperature)
        instance.description = validated_data.get('description', instance.description)
        instance.updated_at = timezone.now()
        instance.save()
        return instance


class CitySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=40)
    country = serializers.CharField(max_length=40)

    def create(self, validated_data):
        city_object = Cities.objects.create(
            name=validated_data['name'],
            country=validated_data['country']
        )
        return city_object


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['notification_period', 'id', 'cities']


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = MyUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password'])
        )
        return user

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'username', 'password']




