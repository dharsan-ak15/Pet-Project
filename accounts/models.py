from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    preferred_pet_type = models.CharField(max_length=10, choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Other', 'Other'), ('None', 'None')], default='None')
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class StaffInviteCode(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="The code string to give to staff members")
    is_active = models.BooleanField(default=True, help_text="Whether this code can still be used")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code

class OTPVerification(models.Model):
    OTP_TYPES = [
        ('Email', 'Email'),
        ('Phone', 'Phone'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.otp_type} OTP for {self.user.username}"
        

class AdminRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_requests')
    message = models.TextField(help_text="Why do you want to become a staff member?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection, if applicable")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Admin Request by {self.user.username}"


class SystemComplaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='system_complaints')
    complaint_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"System Complaint by {self.user.username}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)    

print("Accounts models loaded")