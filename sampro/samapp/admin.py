from django.contrib import admin
from .models import Product,ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # 画像フィールドを1つ追加可能にする

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)