import hashlib
import urllib.parse
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import AddToCartForm, CheckoutForm
from .models import Category, Order, OrderItem, Product

PAYFAST_VALID_IPS = [
    '197.97.145.144',
    '197.97.145.145',
    '197.97.145.146',
    '197.97.145.147',
    '197.97.145.148',
    '197.97.145.149',
    '197.97.145.150',
    '197.97.145.151',
    '41.74.179.194',
    '41.74.179.195',
    '41.74.179.196',
    '41.74.179.197',
    '41.74.179.198',
    '41.74.179.199',
    '41.74.179.200',
    '41.74.179.201',
    '41.74.179.202',
    '41.74.179.203',
    '41.74.179.204',
    '41.74.179.205',
    '41.74.179.206',
    '41.74.179.207',
    '41.74.179.208',
    '41.74.179.209',
    '41.74.179.210',
]


def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def _cart_total(cart):
    return sum(
        Decimal(str(item['price'])) * item['quantity']
        for item in cart.values()
    )


def _generate_signature(data, passphrase=None):
    payload = "&".join(
        f"{k}={urllib.parse.quote_plus(str(v))}"
        for k, v in data.items()
        if v
    )
    if passphrase:
        payload += f"&passphrase={urllib.parse.quote_plus(passphrase)}"
    return hashlib.md5(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Product views
# ---------------------------------------------------------------------------

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    selected_category = None

    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    featured = Product.objects.filter(is_active=True, is_featured=True)[:4]

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'featured_products': featured,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    form = AddToCartForm(initial={'product_id': product.id})
    return render(request, 'store/product_detail.html', {
        'product': product,
        'form': form,
    })


# ---------------------------------------------------------------------------
# Cart views
# ---------------------------------------------------------------------------

def cart_view(request):
    cart = _get_cart(request)
    cart_items = []
    for pid, item in cart.items():
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            continue
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'size': item.get('size', ''),
            'color': item.get('color', ''),
            'price': Decimal(str(item['price'])),
            'line_total': Decimal(str(item['price'])) * item['quantity'],
        })
    total = sum(i['line_total'] for i in cart_items)
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@require_POST
def add_to_cart(request):
    form = AddToCartForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Invalid request.')
        return redirect('store:product_list')

    product = get_object_or_404(Product, id=form.cleaned_data['product_id'], is_active=True)
    cart = _get_cart(request)
    pid = str(product.id)
    quantity = form.cleaned_data['quantity']
    size = form.cleaned_data.get('size', '')
    color = form.cleaned_data.get('color', '')

    if pid in cart:
        cart[pid]['quantity'] = min(cart[pid]['quantity'] + quantity, 10)
    else:
        cart[pid] = {
            'quantity': quantity,
            'size': size,
            'color': color,
            'price': str(product.effective_price),
        }

    _save_cart(request, cart)
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect('store:cart')


@require_POST
def update_cart(request):
    pid = request.POST.get('product_id')
    quantity = request.POST.get('quantity')
    cart = _get_cart(request)
    if pid and pid in cart:
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            qty = 0
        if qty > 0:
            cart[pid]['quantity'] = min(qty, 10)
        else:
            del cart[pid]
        _save_cart(request, cart)
    return redirect('store:cart')


@require_POST
def remove_from_cart(request):
    pid = request.POST.get('product_id')
    cart = _get_cart(request)
    if pid and pid in cart:
        del cart[pid]
        _save_cart(request, cart)
        messages.success(request, 'Item removed from cart.')
    return redirect('store:cart')


# ---------------------------------------------------------------------------
# Checkout & PayFast
# ---------------------------------------------------------------------------

@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('store:cart')

    cart_items = []
    for pid, item in cart.items():
        try:
            product = Product.objects.get(id=pid)
        except Product.DoesNotExist:
            continue
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'size': item.get('size', ''),
            'color': item.get('color', ''),
            'price': Decimal(str(item['price'])),
            'line_total': Decimal(str(item['price'])) * item['quantity'],
        })

    subtotal = sum(i['line_total'] for i in cart_items)
    shipping_cost = Decimal('0.00') if subtotal >= Decimal('500.00') else Decimal('99.00')
    total = subtotal + shipping_cost

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                total=total,
                shipping_name=form.cleaned_data['shipping_name'],
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_postal_code=form.cleaned_data['shipping_postal_code'],
                shipping_phone=form.cleaned_data['shipping_phone'],
            )
            for ci in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=ci['product'],
                    quantity=ci['quantity'],
                    size=ci['size'],
                    color=ci['color'],
                    price=ci['price'],
                )

            # Build PayFast data
            payfast_url = (
                'https://sandbox.payfast.co.za/eng/process'
                if settings.PAYFAST_SANDBOX
                else 'https://www.payfast.co.za/eng/process'
            )
            host = request.get_host()
            scheme = 'https' if request.is_secure() else 'http'

            pf_data = {
                'merchant_id': settings.PAYFAST_MERCHANT_ID,
                'merchant_key': settings.PAYFAST_MERCHANT_KEY,
                'return_url': f'{scheme}://{host}/store/payfast/return/?order={order.order_number}',
                'cancel_url': f'{scheme}://{host}/store/payfast/cancel/?order={order.order_number}',
                'notify_url': f'{scheme}://{host}/store/payfast/notify/',
                'name_first': request.user.first_name or request.user.username,
                'email_address': request.user.email,
                'm_payment_id': order.order_number,
                'amount': f'{total:.2f}',
                'item_name': f'CyberProp Order {order.order_number}',
            }
            pf_data['signature'] = _generate_signature(pf_data, settings.PAYFAST_PASSPHRASE)

            # Clear cart
            _save_cart(request, {})

            return render(request, 'store/payfast_redirect.html', {
                'payfast_url': payfast_url,
                'pf_data': pf_data,
                'order': order,
            })
    else:
        form = CheckoutForm(initial={
            'shipping_name': request.user.get_full_name() or request.user.username,
            'shipping_phone': getattr(request.user, 'phone', ''),
        })

    return render(request, 'store/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
    })


@csrf_exempt
@require_POST
def payfast_notify(request):
    """PayFast ITN (Instant Transaction Notification) handler."""
    pf_data = request.POST.dict()

    # 1. Validate source IP
    sender_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    if ',' in sender_ip:
        sender_ip = sender_ip.split(',')[0].strip()
    if not settings.DEBUG and sender_ip not in PAYFAST_VALID_IPS:
        return HttpResponseBadRequest('Invalid source IP')

    # 2. Verify signature
    received_signature = pf_data.pop('signature', '')
    expected_signature = _generate_signature(pf_data, settings.PAYFAST_PASSPHRASE)
    if received_signature != expected_signature:
        return HttpResponseBadRequest('Invalid signature')

    # 3. Process payment
    order_number = pf_data.get('m_payment_id', '')
    payment_status = pf_data.get('payment_status', '')

    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return HttpResponseBadRequest('Order not found')

    order.payment_id = pf_data.get('pf_payment_id', '')

    if payment_status == 'COMPLETE':
        order.status = 'paid'
    elif payment_status == 'CANCELLED':
        order.status = 'cancelled'
    else:
        order.status = 'pending'

    order.save()
    return HttpResponse('OK')


def payfast_return(request):
    order_number = request.GET.get('order', '')
    return render(request, 'store/payment_success.html', {
        'order_number': order_number,
    })


def payfast_cancel(request):
    order_number = request.GET.get('order', '')
    if order_number:
        Order.objects.filter(order_number=order_number, status='pending').update(status='cancelled')
    return render(request, 'store/payment_cancel.html', {
        'order_number': order_number,
    })


# ---------------------------------------------------------------------------
# Order views
# ---------------------------------------------------------------------------

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})
