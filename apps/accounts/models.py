from django.contrib.auth.models import User
from django.db import models


def profile_upload_path(instance, filename):
    return f"profile_pics/{instance.user.id}/{filename}"


class UserProfile(models.Model):
    """
    Extra profile data for a system user. Contains contact
    details, social links and optional profile image.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    is_moderator = models.BooleanField(default=False)
    about_me = models.TextField(blank=True)
    job = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    twitter = models.URLField(max_length=256, blank=True)
    facebook = models.URLField(max_length=256, blank=True)
    instagram = models.URLField(max_length=256, blank=True)
    linkedin = models.URLField(max_length=256, blank=True)

    profile_image = models.ImageField(
        upload_to=profile_upload_path,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username} Profile"


class AppUser(User):
    class Meta:
        proxy = True

    def __str__(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
