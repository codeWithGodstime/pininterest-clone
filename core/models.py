from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Privacy(models.TextChoices):
    PUBLIC = 'public'
    PRIVATE = 'private'


class Board(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='boards/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    privacy = models.CharField(max_length=20, choices=Privacy.choices, default=Privacy.PRIVATE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    

class Pin(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='pins/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='pins',  null=True, blank=True)
    tags = models.ManyToManyField('Tag', related_name='pins')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.ForeignKey(Pin, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'pin']

    def __str__(self):
        return f"{self.user.username} liked {self.pin.title}"
    
    

