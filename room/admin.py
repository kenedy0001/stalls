from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser
from .forms import UserCreationForm


admin.site.site_header = "Rooms && Stalls Admin"
admin.site.site_title = "Rooms && Stalls Admin"
admin.site.index_title = "Welcome to the Admin Dashboard"

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    model = CustomUser
    list_display = ('phone_number', 'email', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('phone_number',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
from django.contrib import admin
from .models import Room, Stall, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size_in_sq_meters', 'status', 'is_available', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    ordering = ('name',)

@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'room', 'status', 'is_available', 'created_at')
    list_filter = ('status', 'room')
    search_fields = ('number', 'room__name')
    readonly_fields = ('created_at',)
    ordering = ('number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'space_type', 'room', 'stall', 'start_time', 'end_time', 'is_active')
    list_filter = ('space_type', 'is_active', 'start_time')
    search_fields = ('user__username', 'room__name', 'stall__number')
    readonly_fields = ('start_time',)
    ordering = ('-start_time',)
