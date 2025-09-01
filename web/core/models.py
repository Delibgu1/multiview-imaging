from django.contrib.gis.db import models
from django.conf import settings

class Farm(models.Model):
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Field(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    geom = models.PolygonField(srid=4326)

class Project(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    captured_at = models.DateTimeField()

class UploadBatch(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")  # pending|queued|processing|done|error
    keys = models.JSONField(default=list)  # keys S3 enviados

class Job(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    batch = models.ForeignKey(UploadBatch, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="queued")   # queued|running|done|error
    params = models.JSONField(default=dict)
    log = models.TextField(blank=True)

class Asset(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    kind = models.CharField(max_length=20)  # ortho|dem|dsm|pc|mesh
    href = models.URLField()                # URL S3
    cog_href = models.URLField(blank=True)
    tiles_href = models.URLField(blank=True)
    footprint = models.PolygonField(srid=4326, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
