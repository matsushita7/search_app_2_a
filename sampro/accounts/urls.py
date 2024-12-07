from django.urls import path,include
from . import views
app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name="login_view"),
    
]