from django.contrib.auth.models import User
from django.db import models


class PetRequest(models.Model):
    PET_TYPES = [
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
        ('Other', 'Other'),
    ]

    REQUEST_TYPES = [
        ('Lost', 'Lost'),
        ('Found', 'Found'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_requests')
    pet_type = models.CharField(max_length=10, choices=PET_TYPES)
    breed = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    description = models.TextField()
    contact_information = models.CharField(max_length=255)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_type} - {self.pet_type} ({self.breed}) by {self.user.username}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    pet_request = models.ForeignKey(PetRequest, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
