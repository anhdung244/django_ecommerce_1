from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin


from django.views.generic import ListView, DetailView,View
# Create your views here.
from django.utils import timezone
from django.shortcuts import redirect
from .models import Item,OrderItem,Order,BillingAddress

from .forms import CheckoutForm

def products(request):
    context={
        'items':Item.objects.all()
    }
    return render(request,"products.html",context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        #forms
        form=CheckoutForm()
        context={
            'form':form
        }
        return render(self.request, "checkout.html",context)

    def post(self,*args, **kwargs):
        form=CheckoutForm(self.request.POST or None)
        try:
            order=Order.objects.get(user=self.request.user, ordered=False)
        
            if form.is_valid():
                user=form.cleaned_data.get('user')
                street_address=form.cleaned_data.get('street_address')
                apartment_address=form.cleaned_data.get('apartment_address')
                countries=form.cleaned_data.get('countries')
                zip=form.cleaned_data.get('zip')
                # same_shipping_address=form.cleaned_data.get('same_shipping_address')
                # save_info=form.cleaned_data.get('save_info')
                payment_option=form.cleaned_data.get('payment_option')
                billing_address=BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request,'Failed checkout')
            return redirect('core:checkout')

        except ObjectDoesExist:
            messages.error(self.request,"You do not have an active order")
            return redirect('core:checkout')


class HomeView(ListView):
    model=Item
    paginate_by=10
    template_name='home.html'


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={
                'object':order
            }
            return render(self.request, 'order_summary.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")




class ItemDetailView(DetailView):
    model=Item
    template_name='product.html'

@login_required
def add_to_cart(request, slug):
    item=get_object_or_404(Item, slug=slug)
    order_item,created=OrderItem.objects.get_or_create(item=item,user=request.user)
    order_qs=Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request,"This item was updated")
            #them
            return redirect("core:order-summary")
        else: #nếu trong order mà chưa có  order item này thì tạo 1 cái order item mới
            order.items.add(order_item)
            messages.info(request,"This item was added in the order")
            #them
            return redirect("core:order-summary")
    else:# nếu không có query set thì tạo 1 order mới
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This item was updated")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request,slug):
    item=get_object_or_404(Item, slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)

    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request,"This item was removed")
            return redirect("core:order-summary")
        else:
            #add messages
            messages.info(request,"This item was not in your order")
            return redirect("core:order-summary")
            
    else:
        messages.info(request,"You do not have an active order")
        return redirect("core:order-summary")
    

@login_required
def remove_single_item_from_cart(request,slug):
    item=get_object_or_404(Item, slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(user=request.user,item=item,ordered=False)[0]
            if order_item.quantity>1:
                order_item.quantity-=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,'This item was removed')
            return redirect('/order-summary')
        else: 
            messages.info(request,'This item was not in order')  
            return redirect('/order-summary')
    else:
        messages.info(request,'You do not have an active order')
        return redirect('/order-summary')
    


    




