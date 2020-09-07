from django.urls import include, path
from django.conf.urls import url

from .views import ecom, clients, vendors
from django.views.generic import TemplateView


urlpatterns = [
    path('', ecom.home, name='home'),
    path('checkout/', ecom.CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', ecom.ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', ecom.add_to_cart, name='add-to-cart'),
    path('add_coupon/', ecom.AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', ecom.remove_from_cart, name='remove-from-cart'),
    path('Shop/', ecom.ShopView.as_view(), name='shop'),
    path('order-summary/', ecom.OrderSummaryView.as_view(), name='order-summary'),
    path('Produits/Acheter/', ecom.order, name='order'),
    path('remove-item-from-cart/<slug>/', ecom.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment-carte-debit', ecom.PaymentView.as_view(), name='payment'),
    path('payment-paypal/', ecom.paypal, name='paypal'),
    url(r'^payment_done/$', TemplateView.as_view(template_name= "commerce/payment_done.html"), name='payment_done'),
    url(r'^payment_canceled/$', TemplateView.as_view(template_name= "commerce/payment_canceled.html"), name='payment_canceled'),
    path('request-refund/', ecom.RequestRefundView.as_view(), name='request-refund'),

    path('verification/', ecom.bevalide, name='bevalide'),
    path('profile-update/', ecom.ProfileUpdateView.as_view(), name='profile-update'),
    path('Profile/', ecom.profile, name='profile'),
    url(r'About/$', ecom.about, name='about'),
    url(r'Contact/$', ecom.contact, name='contact'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/'r'(?P<post>[-\w]+)/$',ecom.post_detail,name='post_detail'),
    url(r'Blog/$', ecom.post_list, name='blog'),

    path('Clients/', include(([
        path('Acceuil/', clients.view_client, name='view_client'),
        # path('comfirmation/', clients.validate, name='validate'),
    ], 'ecom'), namespace='clients')),

    path('Vendors/', include(([
        path('Dashboard/', vendors.view_vendor, name='view_vendor'),
        path('Add/Products/', vendors.AddProductView.as_view(), name='add_product'),
        path('Products/', vendors.myprod, name='myprod'),
        url(r'^Products/(?P<pk>[0-9]+)/$',vendors.vendpro_detail, name='vendpro_detail'),
        url(r'^Product/(?P<pk>[0-9]+)/update/$',vendors.ProductUpdateView.as_view(), name='vendpro_update'),
        url(r'^Product/(?P<pk>[0-9]+)/delete/$',vendors.ProductDeleteView.as_view(), name='vendpro_delete'),
    ], 'ecom'), namespace='vendors')),
]
