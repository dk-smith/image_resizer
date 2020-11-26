from django.db import models
import uuid

class ImageModel(models.Model):
    id = models.CharField(primary_key=True, max_length=200, blank=False, default=uuid.uuid4)
    status = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', default='')

