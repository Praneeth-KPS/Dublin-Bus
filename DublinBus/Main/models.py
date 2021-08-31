from django.db import models

# Create your models here.
class DublinBikesStatic(models.Model):
    ID = models.IntegerField()
    Number = models.IntegerField()
    Name = models.CharField(max_length=150)
    Address = models.CharField(max_length=150)
    Latitude = models.FloatField()
    Longitude = models.FloatField()