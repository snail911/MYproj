from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)  # Make the user field nullable
    image = models.ImageField(upload_to='images/')
    title = models.CharField(max_length=100)
    last_viewed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the default value if the object is being created
            self.last_viewed = timezone.now()
        return super().save(*args, **kwargs)


class Model(models.Model):
    name = models.CharField(max_length=80, null=True)