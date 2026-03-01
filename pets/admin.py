from django.contrib import admin

from .models import Notification, PetRequest


@admin.action(description='Mark selected requests as Accepted')
def mark_accepted(modeladmin, request, queryset):
    queryset.update(status='Accepted')


@admin.action(description='Mark selected requests as Rejected')
def mark_rejected(modeladmin, request, queryset):
    queryset.update(status='Rejected')

@admin.register(PetRequest)
class PetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'pet_type', 'request_type', 'status', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'pet_request', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
