from django.db import models


class Graph(models.Model):
    path = models.FilePathField('Path to graph', max_length=250, blank=False, null=False, default='~/graph.pb')
    labelsPath = models.FilePathField('Path to labels', max_length=250, blank=False, null=False, default='~/labels.txt')
    date = models.DateTimeField('Graph created', auto_now_add=True)


class Camera(models.Model):
    name = models.CharField('Name of camera', max_length=100)
    longitude = models.DecimalField('Longitude of camera location', decimal_places=10, max_digits=13,
                                    null=True, blank=True)
    latitude = models.DecimalField('Latitude of camera location', decimal_places=10, max_digits=13,
                                   null=True, blank=True)
    streamUrl = models.URLField('Camera stream url', blank=False, null=False)
    isStream = models.BooleanField('Is stream url for this camera stream.', blank=False, null=False, default=True)
    isMjpeg = models.BooleanField('Is stream url for this camera in mjpg format.', blank=False, null=False,
                                  default=False)


class ParkingSpot(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    leftUpperX = models.IntegerField(blank=False, null=False)
    leftUpperY = models.IntegerField(blank=False, null=False)
    rightUpperX = models.IntegerField(blank=False, null=False)
    rightUpperY = models.IntegerField(blank=False, null=False)
    rightLowerX = models.IntegerField(blank=False, null=False)
    rightLowerY = models.IntegerField(blank=False, null=False)
    leftLowerX = models.IntegerField(blank=False, null=False)
    leftLowerY = models.IntegerField(blank=False, null=False)
    rotation = models.FloatField(blank=True, null=True)
    rotatedCordX = models.IntegerField(blank=True, null=True)
    rotatedCordY = models.IntegerField(blank=True, null=True)
    status = models.CharField(blank=True, null=True, max_length=25)
