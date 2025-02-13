from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            phone=phone,
        )
        user.set_password(password)  # Hash password properly
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password=None):
        user = self.create_user(username, email, phone, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)

    objects = CustomUserManager()  # Use custom manager

    def __str__(self):
        return self.username
    
class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=255, null=True, blank=True)
    guest_email = models.EmailField(null=True, blank=True)
    guest_phone = models.CharField(max_length=15, null=True, blank=True)
    destination = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    adults = models.PositiveIntegerField()
    children = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} for {self.destination}"
    

class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Day(models.Model):
    name = models.CharField(max_length=20, unique=True)  # e.g., Monday, Tuesday

    def __str__(self):
        return self.name


class Route(models.Model):
    destination = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, default=1)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.destination} - {self.country.name}"


class RouteTiming(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="timings")
    time = models.TimeField()
    days = models.ManyToManyField(Day)  # A route timing can be on multiple days

    def __str__(self):
        return f"{self.route.destination} at {self.time} on {', '.join([day.name for day in self.days.all()])}"