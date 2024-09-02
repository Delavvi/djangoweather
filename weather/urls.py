from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView, TokenVerifyView
from .api_views import DefaultWeather, SubscriptionChecker, CreateDeleteUpdateGetSubscriptionView, RegisterUser, Check

app_name = "weather"

urlpatterns = [
    path("weather/<str:city>/<str:country>", DefaultWeather.as_view(), name='city_weather_info'),
    path("subscription-checker/", SubscriptionChecker.as_view(), name='subscription-checker'),
    path("subscription/", CreateDeleteUpdateGetSubscriptionView.as_view(), name='subscription'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register', RegisterUser.as_view(), name='register'),
    path('check', Check.as_view(), name='check'),
    ]
