from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, Blog, Comment, Contact, Testimonial, NewsletterSubscription
from django import forms
from django.core.paginator import Paginator

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ['email']

def home(request):
    products = Product.objects.all()[:8]
    testimonials = Testimonial.objects.all()[:5]
    for product in products:
        if product.discount_price and product.discount_price > 0:
            product.discount_percent = int(((product.price - product.discount_price) / product.price) * 100)
        else:
            product.discount_percent = 0
    context = {
        'products': products,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)

def products(request):
    category_slug = request.GET.get('category')
    if category_slug:
        products = Product.objects.filter(category__slug=category_slug)
    else:
        products = Product.objects.all()
    paginator = Paginator(products, 9)  # 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.prefetch_related('products').all()
    context = {
        'products': page_obj,
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'products.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(slug=slug)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product_detail.html', context)

def about(request):
    testimonials = Testimonial.objects.all()[:5]
    context = {'testimonials': testimonials}
    return render(request, 'about.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def blogs(request):
    blogs = Blog.objects.all()
    categories = Category.objects.filter(blogs__isnull=False).distinct()
    recent_blogs = Blog.objects.order_by('-created_at')[:3]
    for blog in blogs:
        blog.tag_list = blog.tags.split(',') if blog.tags else []
    context = {
        'blogs': blogs,
        'categories': categories,
        'recent_blogs': recent_blogs,
    }
    return render(request, 'blogs.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    recent_blogs = Blog.objects.order_by('-created_at').exclude(slug=slug)[:3]
    categories = Category.objects.filter(blogs__isnull=False).distinct()
    # Split tags
    blog.tag_list = blog.tags.split(',') if blog.tags else []
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            comment.save()
            messages.success(request, 'Your comment has been posted!')
            return redirect('blog_detail', slug=blog.slug)
    else:
        comment_form = CommentForm()
    context = {
        'blog': blog,
        'recent_blogs': recent_blogs,
        'categories': categories,
        'comment_form': comment_form,
    }
    return render(request, 'blog_detail.html', context)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author', 'email', 'website', 'content']

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscribed to newsletter successfully!')
            return redirect('home')
    return redirect('home')
