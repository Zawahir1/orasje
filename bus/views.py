from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer
from rest_framework import viewsets
from .models import Booking, Route, Country
from .serializers import BookingSerializer, RouteSerializer
from rest_framework.permissions import IsAuthenticated


class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]  # Allow anyone to create a booking

    def create(self, request, *args, **kwargs):
        """
        Create a new booking. Either guest details (name, email, phone) must be provided.
        """
        guest_name = request.data.get('name')
        guest_email = request.data.get('email')
        guest_phone = request.data.get('phone')

        if not (guest_name and guest_email and guest_phone):
            return Response(
                {"error": "Guest name, email, and phone are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Saves the guest booking
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    def list(self, request):
        countries = Country.objects.prefetch_related('route_set__timings__days').all()
        data = {}

        for country in countries:
            country_name = country.name
            data[country_name] = []

            for route in country.route_set.all():
                route_data = {
                    "destination": route.destination,
                    "days": [],
                    "times": [],
                    "price": route.price
                }

                for timing in route.timings.all():
                    route_data["times"].append(timing.time.strftime("%H:%M"))  # Format time
                    for day in timing.days.all():
                        if day.name not in route_data["days"]:
                            route_data["days"].append(day.name)

                data[country_name].append(route_data)

        return Response(data)
    
    
