from django.urls import path
from . import views


urlpatterns = [
    path('cat/', views.cat, name='cat'),
    path('cat/trade', views.trade, name='trade'),
    path('cat/price', views.price, name='price'),
    path('cat/updown', views.updown, name='updown')
]