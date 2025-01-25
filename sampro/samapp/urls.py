from django.urls import path,include
from . import views
app_name = 'samapp'

urlpatterns = [
    path('',views.search_view, name='search'), #トップページ
    path('product/<int:pk>/', views.product_detail, name='product_detail'), #商品詳細
    path('product/cart/add/<int:product_id>/', views.add_to_cart, name="add_to_cart"),
    path("product/cart/", views.cart_detail, name="cart_detail"),
    path("product/cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/", views.view_cart, name="view_cart"),  # カートを見るページ
    path("cart/clear/", views.clear_cart, name="clear_cart"),#カート情報の削除
    path('cart/update/', views.update_cart, name='update_cart'),
    path('review/<int:product_id>', views.product_review, name='product_review'),#レビュー画面
    path('products/<int:product_id>/purchase/', views.purchase_product, name='purchase_product'),#商品詳細ページ購入
    path('cart/purchase/', views.purchase_cart, name='purchase_cart'),#カートページ購入
    path('products/<int:product_id>/purchase/complete/', views.purchase_complete, name='purchase_complete'),#商品詳細ページ購入完了
    path('cart/purchase/complete/', views.purchase_complete_cart, name='purchase_complete_cart'),#カートページ購入完了
]