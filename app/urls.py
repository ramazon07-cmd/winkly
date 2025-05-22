from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('blogs/', views.blogs, name='blogs'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('newsletter_subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
