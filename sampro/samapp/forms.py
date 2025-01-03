from django import forms
from .models import Product,Review

class SearchForm(forms.Form):#検索ワードのフォーム
    query = forms.CharField(
        label='検索キーワード',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder':'検索したいキーワードを入力'})
        )
    
class ProductForm(forms.ModelForm):#商品追加のフォーム
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category']


class ReviewForm(forms.ModelForm):#レビューのフォーム
    class Meta:
        model = Review
        fields = ['rating', 'purchase_date', 'title', 'content', 'image']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 11)]),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'タイトルを入力'}),
            'content': forms.Textarea(attrs={'placeholder': 'レビュー内容を入力'}),
        }