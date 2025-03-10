from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField()
    is_candidate = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    token = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Candidate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Linking candidate to a user
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name="candidates")
    party = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.party})"
