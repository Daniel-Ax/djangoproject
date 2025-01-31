import os
import uuid

from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    author = models.CharField(max_length=255, null=False)
    subject = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    category = models.CharField(max_length=255, null=False)
    date_posted = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image:
            ext = os.path.splitext(self.image.name)[1]
            unique_filename = f'{uuid.uuid4()}{ext}'
            self.image.name = unique_filename
            super().save(*args, **kwargs)
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
        else:
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.id)])
    
    def contains_text(self, text):
        text = text.lower()
        return text in self.name.lower() or text in str(self.price) or text in self.author.lower() or\
            text in self.subject.lower() or text in self.description.lower() or text in self.category.lower()
