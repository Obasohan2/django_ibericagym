from django.contrib import admin
from .models import ProductCategory, Product, ProductReview, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_on', 'total', 'is_paid')
    list_filter = ('is_paid', 'created_on')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(ProductCategory)
admin.site.register(ProductReview)