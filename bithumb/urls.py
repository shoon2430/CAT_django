from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('userSetting/',views.userSetting, name='userSetting'),
    path('saveUserSetting/',views.saveUserSetting, name='saveUserSetting'),
    path('signup/', views.signup, name='signup'),
    path('cat/', views.cat, name='cat'),
    path('cat/start', views.startTrading, name='startTrading'),
    path('cat/stop', views.stopTrading, name='stopTrading'),
    path('cat/history', views.tradeHistory, name='tradeHistory'),
    path('cat/tickerInfo', views.getTickerInfo, name= 'getTickerInfo'),
    path('cat/backTest', views.getBackTestingResult, name="getBackTestingResult"),
    path('cat/test', views.testing, name="testing"),
]