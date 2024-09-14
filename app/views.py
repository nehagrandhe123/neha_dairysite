from urllib import request
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from .models import OrderPlaced, Payment, Product,Customer,Cart
from django.db.models import Count,Q
from . forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# Create your views here.

@login_required
def home(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, "app/home.html", locals())

@login_required
def about(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, "app/about.html",locals())

@login_required
def contact(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,"app/contact.html",locals())

@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val):
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        product=Product.objects.filter(category=val)
        title=Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())

@method_decorator(login_required,name='dispatch')    
class CategoryTitle(View):
    def get(self,request,val):
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        product=Product.objects.filter(title=val)
        title=Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())

@method_decorator(login_required,name='dispatch')
class ProductDetail(View):
    def get(self,request,pk):
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        product=Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self,request):
        form=CustomerRegistrationForm()
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/customerregistration.html',locals())
    def post(self,request):
        form=CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registered Successfully!! You are an user now..")
        else:
           messages.warning(request,"Data provided is Invalid !!")
        return render(request,'app/customerregistration.html',locals()) 

@method_decorator(login_required,name='dispatch')    
class ProfileView(View):
    def get(self,request):
        form=CustomerProfileForm()
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        return render(request,'app/profile.html',locals())
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            user=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            mobile=form.cleaned_data['mobile']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            
            reg=Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Your Profile is saved Succesfully!!")
        else:
            messages.warning(request,"Data provided is Invalid !!")
        return render(request,'app/profile.html',locals())

@login_required    
def address(request):
    add=Customer.objects.filter(user=request.user)
    totalitem=0
    if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'app/address.html',locals())

@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add=Customer.objects.get(pk=pk)
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        form=CustomerProfileForm(instance=add)
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            add=Customer.objects.get(pk=pk)
            add.name=form.cleaned_data['name']
            add.locality=form.cleaned_data['locality']
            add.city=form.cleaned_data['city']
            add.mobile=form.cleaned_data['mobile']
            add.state=form.cleaned_data['state']
            add.zipcode=form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Updated Succesfully!!")
        else:
            messages.warning(request,"Data provided is Invalid !!")
        return redirect("address")

@login_required        
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id', '').strip('/')
    
    if not product_id.isdigit():
        messages.error(request, "Invalid product ID.")
        return redirect("showcart")
    
    try:
        product = Product.objects.get(id=int(product_id))
        Cart(user=user, product=product).save()
        messages.success(request, "Product added to cart successfully.")
    except Product.DoesNotExist:
        messages.error(request, "Product does not exist.")
    
    return redirect("showcart")


@login_required
def show_cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0
    for p in cart:
        value=p.quantity * p.product.discounted_price
        amount=amount+value
    totalitem=0
    if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
    totalamount=amount+40
    return render(request,'app/addtocart.html',locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        totalitem=0
        if request.user.is_authenticated:
         totalitem=len(Cart.objects.filter(user=request.user))
        famount=0
        for p in cart_items:
            value=p.quantity * p.product.discounted_price
            famount=famount+value
        totalamount=famount+40
        razoramount=int(totalamount*100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

        
        data={"amount":razoramount,"currency":"INR","receipt":"order_rcptid_12"}
        payment_response=client.order.create(data=data)
        print(payment_response)
        #{'amount': 52000, 'amount_due': 52000, 'amount_paid': 0, 'attempts': 0, 'created_at': 1726078479, 'currency': 'INR', 
        # 'entity': 'order', 'id': 'order_OvxEnxzgXwYqOV', 'notes': [], 'offer_id': None, 'receipt': 'order_rcptid_12', 'status': 'created'}
        order_id=payment_response['id']
        order_status=payment_response['status']
        if order_status=='created':
            payment=Payment(
                user=user,
                amount=totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status=order_status
            )
            payment.save()
        return render(request,'app/checkout.html',locals())

@login_required
def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    user=request.user
    customer=Customer.objects.get(id=cust_id)
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid=True
    payment.razorpay_payment_id=payment_id
    payment.save()
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=c.product,
            quantity=c.quantity,
            payment=payment
        )
        c.delete()
    
    return redirect("orders")

@login_required        
def orders(request):
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    order_placed=OrderPlaced.objects.filter(user=request.user)
    return render(request,'app/orders.html',locals())   

@login_required
def plus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity+=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        for p in cart:
            value=p.quantity * p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

@login_required    
def minus_cart(request):
    if request.method=='GET':
        prod_id=request.GET['prod_id']
        c=Cart.objects.get(Q(product=prod_id)& Q(user=request.user))
        c.quantity-=1
        c.save()
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0
        for p in cart:
            value=p.quantity * p.product.discounted_price
            amount=amount+value
        totalamount=amount+40
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
        return JsonResponse(data)

@login_required    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')  # Use .get() to safely get the value
        if prod_id:  # Ensure 'prod_id' is present
            try:
                c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
                c.delete()

                user = request.user
                cart = Cart.objects.filter(user=user)
                amount = 0
                for p in cart:
                    value = p.quantity * p.product.discounted_price
                    amount += value
                totalamount = amount + 40  # Assuming 40 is the shipping or other cost

                data = {
                    'amount': amount,
                    'totalamount': totalamount
                }
                return JsonResponse(data)
            except Cart.DoesNotExist:
                return JsonResponse({'error': 'Product not found in cart'}, status=404)
        else:
            return JsonResponse({'error': 'Product ID not provided'}, status=400)

@login_required
def search(request):
    query=request.GET['search']
    product=Product.objects.filter(Q(title__icontains=query))
    totalitem=0
    if request.user.is_authenticated:
        totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,"app/search.html",locals())
