from paypal.standard.forms import PayPalPaymentsForm
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.core.mail import send_mail, BadHeaderError, mail_admins
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import *
from ..forms import *
from django.urls import reverse_lazy, reverse

from django.contrib import messages

def bevalide(request):
    return render(request, 'commerce/bevalide.html')

def profile(request):
    return render(request, 'commerce/profile.html' )


class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    user_form = UserForm
    profile_form = ProfileForm
    template_name = 'commerce/profile_update.html'

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = ProfileForm(post_data, file_data, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.error(request, 'votre profile est mise-a-jour')
            return HttpResponseRedirect(reverse_lazy('profile'))

        context = self.get_context_data(
                                        user_form=user_form,
                                        profile_form=profile_form
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


def contact(request):
    if request.method == 'POST':
        f = ContactusForm(request.POST)
        if f.is_valid():
            name = f.cleaned_data['name']
            sender = f.cleaned_data['email']
            subject = "You have a new message from {}:{}".format(name, sender)
            message = "Subject: {}\n\nMessage: {}".format(f.cleaned_data['subject'], f.cleaned_data['message'])
            mail_admins(subject, message)

            f.save()
            messages.add_message(request, messages.INFO, 'votre message a été envoyer avec success.')
            return redirect('contact')
    else:
        f = ContactusForm()
    return render(request, 'commerce/contact.html', {'form': f})


def about(request):
    return render(request, 'commerce/about.html')


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_vendor:
            return redirect('vendors:view_vendor')
        if request.user.is_client:
            return redirect('clients:view_client')
        else:
            return redirect('bevalide')
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    items = Item.objects.all()
    paginator = Paginator(items, 8)
    # posts = posts.page(1)
    return render(request, 'commerce/index.html', {
        'items':items,
        'products':Aproduct.objects.all(),
        'posts':posts
    })


@login_required
def post_list(request):
    latest = Post.objects.order_by('-timestamp')[0:3]
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, 6)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'paginate': True
    }
    return render(request, 'commerce/post_list.html', {'posts': posts})

@login_required
def post_detail(request, year, month, day, post):
    posts = Post.objects.all()
    paginator = Paginator(posts, 3)
    # posts = posts.page(1)

    post = get_object_or_404(Post, slug=post)
    comments = post.comments.filter(active=True)
    paginator = Paginator(comments, 7)
    page = request.GET.get('page')
    try:
        comments = paginator.page(page)
    except PageNotAnInteger:
        comments = paginator.page(1)
    except EmptyPage:
        comments = paginator.page(paginator.num_pages)
    context = {
        'comments': comments,
        'paginate': True
    }
    print (comments)
    # for comment in comments:
    #   for reply in comment.replies.all():
    #       print reply.body
    #       # print reply.__dict__

    # rpy = Comment.objects.filter(active=True)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        # user = request.user
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request,'commerce/post_detail.html',
        {'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'posts': posts
        })


# @login_required
# def settings(request):
#     user = request.user

#     try:
#         github_login = user.social_auth.get(provider='github')
#     except UserSocialAuth.DoesNotExist:
#         github_login = None

#     try:
#         twitter_login = user.social_auth.get(provider='twitter')
#     except UserSocialAuth.DoesNotExist:
#         twitter_login = None

#     try:
#         facebook_login = user.social_auth.get(provider='facebook')
#     except UserSocialAuth.DoesNotExist:
#         facebook_login = None

#     can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

#     return render(request, 'ecommerce/settings.html', {
#         'github_login': github_login,
#         'twitter_login': twitter_login,
#         'facebook_login': facebook_login,
#         'can_disconnect': can_disconnect
#     })



################################Autres####################################



from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
import random
import string
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "commerce/payment.html", context)
        else:
            messages.warning(
                self.request, "vous n'avez pas ajouté d'adresse de facturation!?")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token
            )
            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order.ordered = True
            order.payment = payment
            # TODO : assign ref code
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Merci de nous avoir choisi.")
            return redirect("order")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Erreur de limite de débit")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "paramètres invalides")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Pas d'authentification")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Erreur de réseau")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Quelque chose a mal tourné")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(self.request, "Une erreur grave s'est produite")
            return redirect("/")



class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'commerce/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Vous n'avez pas encore choisi aucun de nos produit(s)")
            return redirect("/")

def order(request):
    orders = Order.objects.filter(user=request.user, ordered=True)
    context = {
        'orders': orders
    }
    return render(request, "commerce/confirmation.html", context)


class ShopView(ListView):
    model = Item
    paginate_by = 9
    products = Aproduct.objects.all()
    context = {
        'products': products
    }
    # paginator = Paginator(products, 8)
    template_name = "commerce/shop.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "commerce/product-detail.html"


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "commerce/checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "Vous n'avez pas de commande active")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # add redirect to the selected payment option
                if payment_option == 'CC':
                    return redirect('payment')
                elif payment_option == 'P':
                    return redirect('paypal')
                else:
                    messages.warning(
                        self.request, "Option de paiement non valide")
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "Vous n'avez pas de produit actif")
            return redirect("order-summary")

def paypal(request):
    host = request.get_host()
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '{{order.price}}',
        'item_name': '{{order.title}}',
        'invoice': '{{order.ref_code}}',
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host, reverse('paypal')),
        'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('payment_canceled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'commerce/paypal.html', {'form': form})

def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "commerce/product-detail.html", context)


def shop(request):
    context = {
        'items': Item.objects.all(),
        'product': Aproduct.objects.all()
    }
    return render(request, "commerce/shop.html", context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "La quantité de l'article a été mise à jour.")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "L'article a été ajouté à votre panier.")
            return redirect("order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "L'article a été ajouté à votre panier.")
    return redirect("order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "L'article a été supprimé de votre panier.")
            return redirect("order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "L'article n'était pas dans votre panier.")
            return redirect("product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "vous n'avez pas de produit actif.")
        return redirect("product", slug=slug)
    return redirect("product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "Cette quantité d'articles a été mise à jour.")
            return redirect("order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "L'article n'était pas dans votre panier.")
            return redirect("product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "vous n'avez pas de produit actif.")
        return redirect("product", slug=slug)
    return redirect("product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "Ce coupon n'existe pas")
        return redirect("checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Coupon ajouté avec succès")
                return redirect("checkout")

            except ObjectDoesNotExist:
                messages.info(request, "Vous n'avez pas de produit actif")
                return redirect("checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "commerce/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Votre demande a été reçue")
                return redirect("request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "Cette produit n'existe pas")
                return redirect("request-refund")
