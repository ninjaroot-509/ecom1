from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError
from django.contrib.auth.models import User

from .models import *
from .models import User


class AproductForm(forms.ModelForm):
    class Meta:
        model = Aproduct
        fields = [
        'title',
        'price',
        'category',
        'label',
        'stock',
        'description',
        'image',
    ]

class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ('name', 'body')
        

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio',
            'phone',
            'photo'
        ]

class VendorSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_vendor = True
        if commit:
            user.save()
        return user

class ClientSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_client = True
        if commit:
            user.save()
        return user


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('name', 'body')


class ContactusForm(forms.ModelForm):
 
    class Meta:
        model = Contactus
        fields = '__all__'


#########################Autres######################################


from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('CC', 'Carte de Crédit'),
    ('P', 'PayPal')
)


class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Appartement ou suite',
        'class': 'form-control'
    }))
    ville = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'votre ville actuelle',
        'class': 'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget())

    zip = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Postcode/ZIP',
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'code Promo'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()

