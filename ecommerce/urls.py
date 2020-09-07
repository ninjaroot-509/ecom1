from django.urls import include, path, re_path
from django.contrib import admin
from commerce.views import ecom, clients, vendors

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('commerce.urls')),
    # path('', include('core.urls', namespace='core')),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', ecom.SignUpView.as_view(), name='signup'),
    path('accounts/signup/client/', clients.ClientSignUpView.as_view(), name='client_signup'),
    path('accounts/signup/vendeur/', vendors.VendorSignUpView.as_view(), name='vendor_signup'),
]


admin.site.site_header = "Administration Lohimarket V1.0"
admin.site.site_title = "Lohimarket"
admin.site.index_title = "Bienvenue Admin"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
