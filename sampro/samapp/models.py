from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )  # 親カテゴリを示す

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # カテゴリを単一化

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')  # 保存先を指定

    def __str__(self):
        return f"Image for {self.product.name}"
    
    
    

class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name} ({self.quantity}個)"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)])  # 1～10の選択肢
    purchase_date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='review_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username} - {self.product.name} ({self.rating}/10)"