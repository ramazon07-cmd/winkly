from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Product, Category, Testimonial, Blog, Comment, Contact, NewsletterSubscription, Cart, CartItem, Order, OrderItem
from .forms import ContactForm, CommentForm, NewsletterForm, CartItemForm, BillingForm
from django.db.models import Q

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart

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
    paginator = Paginator(products, 9)
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
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            cart = get_cart(request)
            quantity = form.cleaned_data['quantity']
            size = form.cleaned_data['size']
            CartItem.objects.create(cart=cart, product=product, quantity=quantity, size=size)
            messages.success(request, f"{product.name} added to cart!")
            return redirect('cart')
    else:
        form = CartItemForm(initial={'quantity': 1, 'size': product.sizes.split(',')[0] if product.sizes else ''})
    context = {
        'product': product,
        'related_products': related_products,
        'form': form,
    }
    return render(request, 'product_detail.html', context)

def blogs(request):
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    tag = request.GET.get('tag')
    blogs = Blog.objects.all()
    if query:
        blogs = blogs.filter(Q(title__icontains=query) | Q(content__icontains=query))
    if category_slug:
        blogs = blogs.filter(category__slug=category_slug)
    if tag:
        blogs = blogs.filter(tags__contains=tag)
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

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully subscribed to the newsletter!')
            return redirect('home')
    return redirect('home')

def cart(request):
    cart = get_cart(request)
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        if action == 'update':
            item = get_object_or_404(CartItem, id=item_id, cart=cart)
            form = CartItemForm(request.POST)
            if form.is_valid():
                item.quantity = form.cleaned_data['quantity']
                item.size = form.cleaned_data['size']
                item.save()
                messages.success(request, 'Cart updated!')
        elif action == 'remove':
            item = get_object_or_404(CartItem, id=item_id, cart=cart)
            item.delete()
            messages.success(request, 'Item removed from cart!')
        return redirect('cart')

    cart_items = cart.items.all()
    forms = {item.id: CartItemForm(initial={'quantity': item.quantity, 'size': item.size}) for item in cart_items}
    subtotal = sum(item.get_total() for item in cart_items)
    delivery = 0.00
    discount = 3.00 if subtotal > 0 else 0.00  # Example discount logic
    total = subtotal + delivery - discount

    context = {
        'cart_items': cart_items,
        'forms': forms,
        'subtotal': subtotal,
        'delivery': delivery,
        'discount': discount,
        'total': total,
    }
    return render(request, 'cart.html', context)

def checkout(request):
    cart = get_cart(request)
    cart_items = cart.items.all()
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')

    subtotal = sum(item.get_total() for item in cart_items)
    delivery = 0.00
    discount = 3.00 if subtotal > 0 else 0.00
    total = subtotal + delivery - discount

    if request.method == 'POST':
        form = BillingForm(request.POST)
        if form.is_valid():
            order = Order(
                user=request.user if request.user.is_authenticated else None,
                session_id=request.session.session_key,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                postcode=form.cleaned_data['postcode'],
                payment_method=form.cleaned_data['payment_method'],
                subtotal=subtotal,
                delivery=delivery,
                discount=discount,
                total=total,
            )
            order.save()
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    size=item.size,
                    price=item.product.discount_price if item.product.discount_price else item.product.price,
                )
            cart.items.all().delete()  # Clear cart
            messages.success(request, 'Order placed successfully!')
            return redirect('home')
    else:
        initial = {'email': request.user.email if request.user.is_authenticated else ''}
        form = BillingForm(initial=initial)

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery': delivery,
        'discount': discount,
        'total': total,
    }
    return render(request, 'checkout.html', context)
