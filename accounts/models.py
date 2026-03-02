from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    preferred_pet_type = models.CharField(max_length=10, choices=[('Dog', 'Dog'), ('Cat', 'Cat'), ('Other', 'Other'), ('None', 'None')], default='None')
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username
    

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)    

print("Accounts models loaded")