from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from .models import Profile

User = get_user_model()

@receiver(post_save, sender = User)
def  create_profile(sender, instance, created, **kwargs):
    """
    Signal to creat a profile instance whenever a new User is created
    """

    if created:
        Profile.objects.create(user = instance)

@receiver(post_save, sender = User)
def save_profile(sender, instance, **kwargs):
    """
    Signal to save a Profile instance whenever the user instance is saved
    """
    instance.profile.save()
