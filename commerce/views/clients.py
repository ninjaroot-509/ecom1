from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from ..decorators import client_required
from ..forms import *
from ..models import *

def view_client(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 2)
    items = Item.objects.all()
    paginator = Paginator(items, 8)
    # posts = posts.page(1)
    return render(request, 'commerce/index.html', {
        'items':items,
        'products':Aproduct.objects.all(),
        'posts':posts
    })

class ClientSignUpView(CreateView):
    model = User
    form_class = ClientSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'client'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('clients:view_client')

