from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser, PermissionsMixin
from django.utils import timezone


class Timezone(models.Model):
    timezone = models.CharField(max_length=10)
    id = models.AutoField(primary_key=True)


class Cities(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=20, default=None)

    class Meta:
        db_table = "City"


class WeatherData(models.Model):
    id = models.AutoField(primary_key=True)
    temperature = models.FloatField(default=None)
    description = models.CharField(max_length=50, default='common')
    icon = models.CharField(max_length=20, default='01d')
    city = models.OneToOneField(Cities, related_name='city', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"WeatherData for {self.city.name} at {self.created_at}"

    class Meta:
        db_table = "Weather"


class Subscription(models.Model):
    notification_period = models.IntegerField(choices=[(1, '1 hour'), (3, '3 hours'), (6, '6 hours'), (12, '12 hours')])
    id = models.AutoField(primary_key=True)
    cities = models.ManyToManyField(Cities, related_name='cities')


class MyUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password, **extra_fields)


class MyUser(AbstractUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    object = MyUserManager
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    subscription = models.ManyToManyField(Subscription, related_name='users')
    timezone = models.ForeignKey(Timezone, related_name='users', on_delete=models.SET_DEFAULT, default=None, blank=True,
                                 null=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'User'

