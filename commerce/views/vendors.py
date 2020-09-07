from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..decorators import vendor_required
from ..forms import *
from ..models import *
from django.views.generic import TemplateView

@login_required
def view_vendor(request):
    return render(request, 'commerce/vendors/succ.html')


# @login_required
# def add_products(request):
#     return render(request, 'commerce/vendors/add_products.html')

@method_decorator([login_required, vendor_required], name='dispatch')
class AddProductView(LoginRequiredMixin, CreateView):
    model = Aproduct
    success_url = '/Vendors/Products/'
    template_name = 'commerce/vendors/add_products.html'
    fields = [
        'title',
        'price',
        'category',
        'label',
        'stock',
        'description',
        'image',
    ]
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.author:
            return True
        return False

class ProductUpdateView(UpdateView):
    model = Aproduct
    template_name = 'commerce/vendors/editprod.html'
    success_url = '/Vendors/Products/'
    fields = [
        'title',
        'price',
        'category',
        'label',
        'stock',
        'description',
        'image',
    ]
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        product = self.get_object()
        if self.request.user == product.author:
            return True
        return False
    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     return queryset.filter(author=self.request.user)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'commerce/vendors/product_delete.html'
    model = Aproduct
    success_url = reverse_lazy('vendors:myprod')
        
class VendorSignUpView(CreateView):
    model = User
    form_class = VendorSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'vendor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('vendors:view_vendor')

@login_required
def myprod(request):
    products = Aproduct.objects.all()
    items = Item.objects.all()
    return render(request, 'commerce/vendors/myprod.html', {'products':products,'items':items})

@login_required
def vendpro_detail(request, pk):
    # products = Aproduct.objects.all()
    # paginator = Paginator(products, 3)
    # # products = products.page(1)
    product = get_object_or_404(Aproduct, pk=pk)
    messages = product.messages.order_by('created')[0:3]
    paginator = Paginator(messages, 4)
    page = request.GET.get('page')
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    context = {
        'messages': messages,
        'paginate': True
    }
    print (messages)
    # for comment in messages:
    #   for reply in comment.replies.all():
    #       print reply.body
    #       # print reply.__dict__

    # rpy = Comment.objects.filter(active=True)
    if request.method == 'POST':
        message_form = MessageForm(data=request.POST)
        if message_form.is_valid():
            new_message = message_form.save(commit=False)
            # Assign the current post to the message
            new_message.product = product
            # Save the message to the database
            new_message.save()
    else:
        message_form = MessageForm()
    return render(request,'commerce/vendors/vendpro_detail.html', 
        {'product': product,
        'items':Item.objects.all(),
        'messages': messages,
        'message_form': message_form})
