from django.db import models
from main.models import TimeStampedModel
from django.contrib.auth import get_user_model

from cart.models import CartItem

User = get_user_model()

ORDER_CHOICES = (("pending", "pending"), ("completed", "completed"))

class Order(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ORDER_CHOICES)
    is_paid = models.BooleanField(default=False)


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        CartItem, related_name="product_order", on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
