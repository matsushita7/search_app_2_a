from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.core.cache import cache
from .models import Product, Category, Review, Purchase


def update_bestseller_ranking():#過去30日の売上ランキング計算キャッシュ
    """
    売れ筋ランキングを計算してキャッシュに保存
    """
    one_month_ago = now() - timedelta(days=30)

    ranking = (
        Purchase.objects.filter(purchase_date__gte=one_month_ago)
        .values('product__id', 'product__name', 'product__price', 'product__description')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )

    
    ranked_products = []
    for item in ranking:
        product = Product.objects.get(id=item['product__id'])
        first_image = product.images.first()  # 最初の画像を取得

        ranked_products.append({
            'product_id': item['product__id'],
            'product_name': item['product__name'],
            'product_price': item['product__price'],
            'product_description': item['product__description'],
            'total_quantity': item['total_quantity'],
            'product_img': first_image.image.url if first_image else None,  # 最初の画像のURL
        })
    
    # キャッシュに保存（次回更新まで保持）
    cache.set('bestseller_ranking', ranked_products, timeout=86400)  # 24時間
    
    cached_data = cache.get('bestseller_ranking')
    print("キャッシュに保存されたデータ:", cached_data)
