from django.db import models

# Категории
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# Товары
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    # Главное фото
    def main_image(self):
        return self.images.filter(is_main=True).first()

    # Процент скидки
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((self.old_price - self.price) / self.old_price * 100)
        return 0


# Галерея изображений
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"