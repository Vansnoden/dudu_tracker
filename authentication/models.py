from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname  = models.CharField("Full Name", max_length=200, blank=False)
    phone    = models.CharField("Phone", max_length=100, blank=True)
    picture  = models.ImageField(upload_to='uploads/profile_images/',blank=True)
    
    def __str__(self):
        return self.user.username