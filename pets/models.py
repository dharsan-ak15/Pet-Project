from django.contrib.auth.models import User
from django.db import models


class PetRequest(models.Model):
    PET_TYPES = [
        ('Bird', 'Bird'),
        ('Cat', 'Cat'),
        ('Chinchilla', 'Chinchilla'),
        ('Dog', 'Dog'),
        ('Ferret', 'Ferret'),
        ('Gerbil', 'Gerbil'),
        ('Guinea Pig', 'Guinea Pig'),
        ('Hamster', 'Hamster'),
        ('Mouse', 'Mouse'),
        ('Rabbit', 'Rabbit'),
        ('Reptile', 'Reptile'),
        ('Other', 'Other'),
    ]

    REQUEST_TYPES = [
        ('Lost', 'Lost'),
        ('Found', 'Found'),
        ('Adoption', 'Adoption'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Reunited', 'Reunited'),
    ]

    GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Couple/Both', 'Couple/Both'),
    ]

    SIZE_CHOICES = [
    ('Small', 'Small'),
    ('Medium', 'Medium'),
    ('Large', 'Large'),
    ]

    AGE_UNIT_CHOICES = [
        ('Months', 'Months'),
        ('Years', 'Years'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_requests')
    pet_type = models.CharField(max_length=20, choices=PET_TYPES)
    breed = models.CharField(max_length=100)
    color = models.CharField(max_length=100)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    age_unit = models.CharField(max_length=10, choices=AGE_UNIT_CHOICES, default='Years')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    location = models.CharField(max_length=255)
    description = models.TextField()
    contact_information = models.CharField(max_length=255)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES)
    
    # Adoption Specific Fields
    VACCINATION_CHOICES = [
        ('Fully Vaccinated', 'Fully Vaccinated'),
        ('Partially Vaccinated', 'Partially Vaccinated'),
        ('Not Vaccinated', 'Not Vaccinated'),
        ('Unknown', 'Unknown'),
    ]
    vaccination_status = models.CharField(max_length=30, choices=VACCINATION_CHOICES, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True, help_text="List any known medical illnesses or diseases.")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    is_verified_vet = models.BooleanField(default=False)
    image = models.ImageField(upload_to='pets/', blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection, if applicable")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.request_type} - {self.pet_type} ({self.breed}) by {self.user.username}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    pet_request = models.ForeignKey(PetRequest, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class Comment(models.Model):
    pet_request = models.ForeignKey(PetRequest, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.pet_request}"


class ReportAbuse(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abuse_reports')
    pet_request = models.ForeignKey(PetRequest, on_delete=models.CASCADE, related_name='abuse_reports', blank=True, null=True)
    reason = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='abuse_reports/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = f"Pet #{self.pet_request.id}" if self.pet_request else "General Site Report"
        return f"Abuse Report by {self.reporter.username} on {target}"


class PetContactRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    REASON_CHOICES = [
        ('I found this pet', 'I found this pet'),
        ('This might be my lost pet', 'This might be my lost pet'),
        ('I want to adopt this pet', 'I want to adopt this pet'),
        ('Other', 'Other'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_requests_made')
    pet = models.ForeignKey(PetRequest, on_delete=models.CASCADE, related_name='contact_requests_received')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    message = models.TextField()
    image = models.ImageField(upload_to='contact_requests/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection, if applicable")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Contact Request by {self.requester.username} for {self.pet}"
