# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class ImageModel(models.Model):
	image = models.ImageField()

class FacebookID(models.Model):
	pi_id = models.CharField(unique=True,max_length=200)
	fb_id = models.CharField(max_length=200)

class Pi(models.Model):
	fb_id = models.CharField(unique=True,max_length=200)
	kill = models.BooleanField(default=False)

class Live(models.Model):
	fb_id = models.CharField(unique=True,max_length=200)
	live = models.BooleanField(default=False)