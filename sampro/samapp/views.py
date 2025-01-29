from django.shortcuts import render, get_object_or_404, redirect 
from .models import Product, Category, Review, Purchase
from .forms import ProductForm, SearchForm, ReviewForm
from django.core.paginator import Paginator 
from django.db.models import Q,Sum
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, timedelta
from django.core.cache import cache




def product_create(request): 
    if request.method == 'POST': 
        form = ProductForm(request.POST) 
        if form.is_valid(): 
            form.save() 
            return redirect('product_list') 
    else: 
        form = ProductForm() 
    return render(request, 'product_form.html', {'form': form}) 

def product_detail(request, pk): #商品詳細画面表示
    product = get_object_or_404(Product, pk=pk) 
    return render(request, 'product_detail.html', {'product': product}) 

def product_update(request, pk): 
    product = get_object_or_404(Product, pk=pk) 
    if request.method == 'POST': 
        form = ProductForm(request.POST, instance=product) 
        if form.is_valid(): 
            form.save() 
            return redirect('product_detail', pk=product.pk) 
    else: 
        form = ProductForm(instance=product) 
# product オブジェクトをテンプレートに渡す 
    return  render(request,  'product_form.html',  {'form':  form,  'product': product})

def product_delete(request, pk): 
    product = get_object_or_404(Product, pk=pk) 
    if request.method == 'POST': 
        product.delete() 
        return redirect('product_list') 
    return render(request, 'product_confirm_delete.html', {'product': product}) 

def product_list(request): 
    products = Product.objects.all() 
    return render(request, 'product_list.html', {'products': products}) 

def search_view(request): 
    query = request.GET.get('query', '')
    form = SearchForm(request.GET or None) 
    category_id = request.GET.get('category', '')  # カテゴリIDを取得
    categories = Category.objects.filter(parent=None).prefetch_related('children')
    subcategories = []  # 子カテゴリを格納するリスト
    results = Product.objects.all()  # クエリセットの初期化 
    TAX_RATE = Decimal(0.1)#税金
    
    if form.is_valid(): #ワード検索フィルタリング
        query = form.cleaned_data['query'] 
        if query: 
            results = results.filter(name__icontains=query)

    # カテゴリフィルタリング 
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            if selected_category.parent is None:
                # 大カテゴリの場合、その子カテゴリも含めて検索
                subcategories = Category.objects.filter(parent=selected_category)
                results = results.filter(category__in=subcategories) | results.filter(category=selected_category)
            else:
                # 小カテゴリの場合、直接そのカテゴリで検索
                results = results.filter(category=selected_category)
        except Category.DoesNotExist:
            results = results.none()
            
    # 最低価格・最高価格のフィルタリング
    min_price = request.GET.get('min_price') 
    max_price = request.GET.get('max_price')
    if min_price: 
        results = results.filter(price__gte=min_price) 
    if max_price: 
        results = results.filter(price__lte=max_price) 

    price_ranges = request.GET.getlist('price_range')
    if price_ranges:
        # 価格帯でフィルタリング
        price_filters = []
        for range_ in price_ranges:
            if '-' in range_:
                start, end = range_.split('-')
                if end:  # 上限あり
                    price_filters.append({'price__gte': start, 'price__lte': end})
                else:  # 上限なし
                    price_filters.append({'price__gte': start})
        combined_filter = Q()
        for price_filter in price_filters:
            combined_filter |= Q(**price_filter)
        results = results.filter(combined_filter)

    # 並び替え処理 
    sort_by = request.GET.get('sort', 'name') 
    if sort_by == 'price_asc': 
        results = results.order_by('price') 
    elif sort_by == 'price_desc': 
        results = results.order_by('-price') 
    #resultsのデータをいじる
    # クエリセットをリストに変換せず、直接Paginatorに渡す 
    paginator = Paginator(results,20)
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number)
    results_count = results.count()

    for product in page_obj:
        product.tax_included_price = round(product.price * (1 + TAX_RATE), 2)

    # 過去30日の売れ筋ランキング表示
    ranked_products = cache.get('bestseller_ranking', [])
    print(ranked_products)
    if not ranked_products:
        # ランキングがキャッシュに存在しない場合は空のリストを返す
        ranked_products = []
        print("入ってない")

    context = {
        'page_obj':page_obj,
        'form':form,
        'results':results,
        'results_count':results_count,
        'query':query,
        'category_id':category_id,#カテゴリネームだったもの。変数名が変わってる
        'min_price':min_price,
        'max_price':max_price,
        'sort_by':sort_by,
        'price_ranges': price_ranges,
        'subcategories': subcategories,
        'categories':categories,
        'ranked_products': ranked_products,
    }

    return render(request, 'search.html', context)


def add_to_cart(request, product_id):
    # 商品を取得
    product = get_object_or_404(Product, id=product_id)

    # セッションからカートを取得、または新しいカートを作成
    cart = request.session.get("cart", {})

    # POSTから個数を取得（デフォルト値は1）
    quantity = int(request.POST.get("quantity", 1))

    # 商品が既にカートにある場合、数量を増加
    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] += quantity
    else:
        # 商品をカートに追加
        cart[str(product_id)] = {
            "name": product.name,
            "quantity": quantity,
            "price": float(product.price),
        }

    # セッションを更新
    request.session["cart"] = cart
    messages.success(request, f"{product.name}をカートに追加しました！")

    return render(request, 'cart_added.html', {'product': product})
    # return redirect("samapp:product_detail", pk=product_id)


def cart_detail(request):
    # セッションからカートを取得、存在しない場合は空の辞書
    cart = request.session.get("cart", {})
    total_price = sum(item["price"] * item["quantity"] for item in cart.values())

    return render(request, "cart_detail.html", {"cart": cart, "total_price": total_price})


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})

    # カートから商品を削除
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session["cart"] = cart
        messages.success(request, "商品をカートから削除しました！")

    return redirect("cart_detail")

def view_cart(request):
    # セッションからカートを取得、空の場合は空の辞書を渡す
    cart = request.session.get("cart", {})

    # カートの合計金額を計算
    total_price = sum(item["quantity"] * item["price"] for item in cart.values())

    context = {
        "cart": cart,
        "total_price": total_price,
    }
    return render(request, "cart.html", context)



def clear_cart(request):
    # カートをクリア
    
    request.session["cart"] = {}
    messages.info(request, "カートを空にしました。")
    return redirect("samapp:view_cart")



def update_cart(request):
    if request.method == "POST":
        cart = request.session.get("cart", {})

        for product_id in cart.keys():
            # 各商品の数量を更新
            new_quantity = int(request.POST.get(f"quantity_{product_id}", cart[product_id]["quantity"]))
            cart[product_id]["quantity"] = new_quantity

        # セッションを更新
        request.session["cart"] = cart
        messages.success(request, "カートを更新しました！")

    return redirect("samapp:view_cart")

@login_required
def product_review(request, product_id): #レビュー機能
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.reviewer = request.user
            review.save()
            return redirect('samapp:product_detail', pk=product_id)
    else:
        form = ReviewForm()

    return render(request, 'product_review.html', {'form': form, 'product': product})

@login_required
def purchase_product(request, product_id):#商品詳細ページからの商品購入データ受け取り
    """
    商品詳細ページから1つの商品を購入
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # 購入処理
        quantity = int(request.POST.get('quantity', 1))
        total_price = product.price * quantity
        Purchase.objects.create(
            product=product,
            buyer=request.user,
            quantity=quantity,
            total_price=total_price
        )
        return redirect('samapp:purchase_complete', product_id=product_id)

    # 確認画面
    return render(request, 'confirm_purchase.html', {
        'product': product,
        'quantity': 1,
    })

@login_required
def purchase_cart(request):
    """
    カート内の商品を一括購入
    """
    cart = request.session.get('cart', {})
    purchases = []
    total_price = 0

    if request.method == 'POST':
        # 購入処理
        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            quantity = item['quantity']
            total_price += product.price * quantity
            purchases.append(Purchase(
                product=product,
                buyer=request.user,
                quantity=quantity,
                total_price=product.price * quantity
            ))
        Purchase.objects.bulk_create(purchases)

        # カートを空にする
        request.session['cart'] = {}
        return redirect('samapp:purchase_complete_cart')

    # 確認画面用データ
    cart_products = []
    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        cart_products.append({
            'product': product,
            'quantity': item['quantity'],
            'total_price': product.price * item['quantity'],
        })

    return render(request, 'confirm_purchase_cart.html', {
        'cart_products': cart_products,
        'total_price': sum(item['total_price'] for item in cart_products),
    })


def purchase_complete(request, product_id=None):
    """
    購入完了画面
    """
    product = get_object_or_404(Product, id=product_id) if product_id else None
    return render(request, 'purchase_complete.html', {'product': product})


def purchase_complete_cart(request):
    """
    カート購入完了画面
    """
    return render(request, 'purchase_complete_cart.html')

def account_show_view(request):
    products = Product.objects.all() 
    return render(request, 'account_show.html') 

#　購入が押された商品のデータを入手し、売れ筋ランキングや、管理者画面から在庫追加した方がいいものを見れるようにする。
# 検索数トップも作る
#　在庫がない場合、「発送が遅れる場合があります」という表記が出る。