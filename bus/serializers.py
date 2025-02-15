from rest_framework import serializers
from .models import CustomUser, Booking, Route, Country, RouteTiming, Day
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password']

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)

class LoginSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()  # Accepts email or username
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get("username")  # Can be username or email
        password = attrs.get("password")

        user = CustomUser.objects.filter(email=username_or_email).first()
        if user:
            username_or_email = user.username  # Convert email to username

        user = authenticate(username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError({"error": "Invalid credentials"})

        tokens = super().validate(attrs)
        return {
            "user": UserSerializer(user).data,
            "access": tokens["access"],
            "refresh": tokens["refresh"]
        }
        
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        
        


class RouteTimingSerializer(serializers.ModelSerializer):
    days = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=Day.objects.all()
    )

    class Meta:
        model = RouteTiming
        fields = ['time', 'days']


class RouteSerializer(serializers.ModelSerializer):
    timings = RouteTimingSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['destination', 'timings', "price"]


class CountryRoutesSerializer(serializers.ModelSerializer):
    routes = RouteSerializer(many=True, source='route_set')

    class Meta:
        model = Country
        fields = ['name', 'routes']