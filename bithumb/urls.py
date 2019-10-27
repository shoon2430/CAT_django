from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('cat/', views.cat, name='cat'),
    path('cat/start', views.startTrading, name='startTrading'),
    path('cat/stop', views.stopTrading, name='stopTrading')
]