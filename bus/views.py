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
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from django.utils.timezone import make_aware
from rest_framework.decorators import action
from datetime import datetime, timedelta





class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Save user and get the instance
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({
                "message": "User registered successfully!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "phone": user.phone,
                },
                "refresh": str(refresh),
                "access": access_token
            }, status=status.HTTP_201_CREATED)
        
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
        username = request.data.get('username')
        print(request.data)
        
        if username:
            user = CustomUser.objects.filter(username=username).first()
            if not user:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )

            request.data['user'] = user.id

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()  # Saves the user booking
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not (guest_name and guest_email and guest_phone):
            return Response(
                {"error": "Guest name, email, and phone are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data['guest_email'] = guest_email
        request.data['guest_phone'] = guest_phone
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Saves the guest booking
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request, *args, **kwargs):
        """
        Retrieve bookings based on user or guest details.
        - If 'username' is provided, return all bookings made by that user.
        - If 'email' and 'phone' are provided, return all bookings made by that guest.
        - The results are sorted by 'date' and 'time'.
        """
        username = request.query_params.get("username")
        guest_email = request.query_params.get("email")
        guest_phone = request.query_params.get("phone")

        if username:
            user = CustomUser.objects.filter(username=username).first()
            if not user:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )
            bookings = Booking.objects.filter(user=user).order_by("date", "time")

        elif guest_email and guest_phone:
            bookings = Booking.objects.filter(guest_email=guest_email, guest_phone=guest_phone).order_by("date", "time")

        else:
            return Response(
                {"error": "Provide either 'username' or 'email' and 'phone'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(bookings, many=True)
        booking_data = serializer.data

    # Manually add user email and phone if a user is associated with the booking
        for booking in booking_data:
            booking_obj = bookings.get(id=booking["id"])  # Get the actual booking object
            if booking_obj.user:  # If there's a user linked to the booking
                booking["user_email"] = booking_obj.user.email
                booking["user_phone"] = booking_obj.user.phone
            else:
                booking["user_email"] = booking_obj.guest_email
                booking["user_phone"] = booking_obj.guest_phone
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=True, methods=['DELETE'])
    def check_and_delete(self, request, pk=None):
        """
        Check if departure is within 24 hours before deleting a booking.
        - If departure time is in less than 24 hours, return a message.
        - Otherwise, delete the booking.
        """
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Convert departure time to an aware datetime
        current_time = make_aware(datetime.now())
        departure_time = make_aware(datetime.combine(booking.date, booking.time))
        time_difference = departure_time - current_time

        if time_difference <= timedelta(hours=24):
            return Response(
                {"message": "Cannot delete this booking as departure is within 24 hours."},
                status=status.HTTP_403_FORBIDDEN
            )

        booking.delete()
        return Response(
            {"message": "Booking deleted successfully."}, status=status.HTTP_200_OK
        )
class RouteViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        countries = Country.objects.prefetch_related('route_set__timings__days').all()
        data = {}

        for country in countries:
            country_name = country.name
            data[country_name] = []

            for route in country.route_set.all():
                # Dictionary to group times by their corresponding days
                days_times_map = {}

                for timing in route.timings.all():
                    time_str = timing.time.strftime("%H:%M")  # Convert time to string
                    for day in timing.days.all():
                        if day.name not in days_times_map:
                            days_times_map[day.name] = []
                        days_times_map[day.name].append(time_str)

                # Format data to match the required structure
                route_data = {
                    "destination": route.destination,
                    "days": list(days_times_map.keys()),  # Extract unique days
                    "times": list({time for times in days_times_map.values() for time in times}),  # Unique times
                    "schedule": [{ "day": day, "times": times } for day, times in days_times_map.items()],  # List of days with times
                    "price": route.price
                }

                data[country_name].append(route_data)

        return Response(data)