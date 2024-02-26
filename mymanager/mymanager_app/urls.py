from django.conf.urls import include
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginP, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logoutP, name='logout'),

    # action views
    path('changePaypal/', views.changePaypalEmail, name='changePaypal'),
    path('uploadRemoAccount/', views.uploadRemoAccount, name='uploadRemoAccount'),
    path('accountPerformance/', views.accountPerformance, name='accountPerformance'),
    path('getPerformance/', views.getPerformance, name='getPerformance'),
    path('withdrawBalance/', views.withdrawBalance, name='withdrawBalance'),

]
