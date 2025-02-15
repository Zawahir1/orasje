from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Booking, Country, Route, RouteTiming, Day

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)

class RouteAdmin(admin.ModelAdmin):
    list_display = ('destination', 'country', 'price')
    search_fields = ('destination', 'country__name')
    list_filter = ('country',)

admin.site.register(Route, RouteAdmin)

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    save_as = True

admin.site.register(Country, CountryAdmin)

class RouteTimingAdmin(admin.ModelAdmin):
    list_display = ('route', 'time', 'get_days')
    search_fields = ('route__destination',)
    list_filter = ('route', 'days')

    def get_days(self, obj):
        return ", ".join([day.name for day in obj.days.all()])
    get_days.short_description = 'Days'

    def save_model(self, request, obj, form, change):
        obj.save()  # Save RouteTiming first before adding ManyToMany data
        form.save_m2m()  # Save ManyToMany relationships (days)

admin.site.register(RouteTiming, RouteTimingAdmin)



class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'destination', 'user_email', 'user_phone', 'guest_name', 'guest_email', 'guest_phone', 'date', 'time', 'price')
    search_fields = ('user__email', 'user__phone', 'guest_email', 'guest_phone')
    list_filter = ('destination', 'date')

    def user_email(self, obj):
        return obj.user.email if obj.user else "Guest"
    user_email.short_description = "User Email"

    def user_phone(self, obj):
        return obj.user.phone if obj.user else "Guest"
    user_phone.short_description = "User Phone"

    class Media:
        js = ('admin/js/print_table.js',)  # Add custom JavaScript for printing

admin.site.register(Booking, BookingAdmin)
