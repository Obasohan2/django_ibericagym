from django.db import models
from django.contrib.auth.models import User


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Product Categories"


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True) # For SEO-friendly URLs
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)  # Up to 999,999.99 if needed
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Prevent duplicate reviews per user-product

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating}★)"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

