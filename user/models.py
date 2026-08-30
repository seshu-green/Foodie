from django.db import models
from django.contrib.auth.models import User

# ----------------- USER PROFILE -----------------

class users(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=128, unique=True)

    dob = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# ----------------- CHAT HISTORY -----------------

class chats(models.Model):
    name = models.CharField(max_length=128, default='***')
    count = models.IntegerField(default=1)
    prompt = models.CharField(max_length=128, default='***')
    bot = models.TextField(default='***')

    image = models.ImageField(
        upload_to="chat_images/",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['count']

    def __str__(self):
        return f"{self.name} #{self.count}"
    
# Paste it right here!
class Disease(models.Model):
    info = models.TextField(default='lunch')
    type=models.CharField(max_length=129, default='lunch')
    name = models.TextField(default='lunch')
    symptoms = models.TextField()
    medicines = models.TextField()
    f2avoid = models.TextField(default='nkj')

    def __str__(self):
        return self.name

