from django.db import models

class Food(models.Model):
    type = models.CharField(max_length=128, default='lunch')
    info = models.CharField(max_length=129, default='lunch')
    item = models.CharField(max_length=128)
    variant = models.CharField(max_length=128)
    method = models.TextField()
    nutrients = models.TextField()
    benefits = models.TextField()
    hazards = models.TextField()
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.item} - {self.variant}"