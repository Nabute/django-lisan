from django.db import models
from lisan import LisanModelMixin


class SomeModel(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')


class TestModel(LisanModelMixin, models.Model):
    lisan_fields = ['title', 'description']
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    some = models.ForeignKey(
        SomeModel, null=True, blank=True, on_delete=models.CASCADE)
    author = models.CharField(
        max_length=100, blank=True, null=True, default='')


class TheOtherModel(models.Model):
    name = models.CharField(max_length=100, blank=True, default='')
    title = models.CharField(max_length=100, blank=True, default='')
    model_link = models.ForeignKey(
        TestModel, null=True, blank=True, on_delete=models.CASCADE)
