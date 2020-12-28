from django.db import models


class Company(models.Model):

    name = models.CharField(max_length=64)
    address = models.CharField(max_length=128)


class Person(models.Model):

    name = models.CharField(max_length=64)
    phone = models.CharField(max_length=12)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='persons')