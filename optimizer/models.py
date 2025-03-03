from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link product to a user
    name = models.CharField(max_length=100)  # Name of the product
    demand = models.IntegerField()  # Demand for the product
    supply = models.IntegerField()  # Supply of the product
    cost = models.IntegerField()  # Cost per unit
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return self.name