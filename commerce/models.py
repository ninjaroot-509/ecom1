from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.dispatch import receiver
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField


class User(AbstractUser):
    is_client = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)

# Create your models here.
CATEGORY_CHOICES_VEND = (
    ('SB', 'Shirts And Blouses'),
    ('TS', 'T-Shirts'),
    ('EL', 'Electroniques'),
    ('VL', 'Valise'),
    ('VT', 'Voiture'),
    ('TR', 'Terrain'),
    ('BJ', 'Bijoux')
)


LABEL_CHOICES_VEND = (
    ('V', 'Vente'),
    ('N', 'nouveau'),
    ('P', 'promotion')
)

AVAILIBILITY_CHOICES_VEND = (
    ('D', 'disponible'),
    ('I', 'indisponible'),
    ('PT', 'presque terminé'),
)

class Aproduct(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.CharField(choices=CATEGORY_CHOICES_VEND, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES_VEND, max_length=1)
    stock = models.CharField(choices=AVAILIBILITY_CHOICES_VEND, max_length=2)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='Vendors/produits/%Y/%m/%d')
    author = models.ForeignKey(User,related_name='produits_auth', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse('vendpro_detail', kwargs={'pk': self.pk})

class Message(models.Model):
    product = models.ForeignKey(Aproduct, related_name='messages', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Nouveau message par {} Apropos du produit {}'.format(self.name, self.product)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=12, blank=True)
    # address = models.ForeignKey(BillingAddress, on_delete=models.CASCADE)
    facebook = models.CharField(max_length=200)
    whatsapp = models.CharField(max_length=200)
    github = models.CharField(max_length=200)
    linkedin = models.CharField(max_length=200)
    instagram = models.CharField(max_length=200)
    photo = models.ImageField(default='photo.jpg', upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset().filter(status='published')

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),('published', 'Published'),)

    title = models.CharField(max_length=250)
    post_logo = models.ImageField(upload_to='posts_pics/')
    slug = models.SlugField(max_length=250,unique_for_date='created_on')
    author = models.ForeignKey(User,related_name='blog_posts', on_delete=models.CASCADE)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES, default='published')
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ('-created_on',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail',args=[self.created_on.year,self.created_on.strftime('%m'),self.created_on.strftime('%d'),self.slug])

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    # reply_to = models.ForeignKey('self', related_name='replies',null=True, blank=True, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, related_name='comments_profile', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class Contactus(models.Model):
    name = models.CharField(max_length=200, help_text="Name of the sender")
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name_plural = "Contactus"
 
    def __str__(self):
        return self.name + "-" +  self.email


# type models here.
CATEGORY_CHOICES = (
    ('SB', 'Shirts And Blouses'),
    ('TS', 'T-Shirts'),
    ('EL', 'Electroniques'),
    ('VL', 'Valise'),
    ('VT', 'Voiture'),
    ('TR', 'Terrain'),
    ('BJ', 'Bijoux')
)

LABEL_CHOICES = (
    ('V', 'Vente'),
    ('N', 'nouveau'),
    ('P', 'promotion')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

AVAILIBILITY_CHOICES = (
    ('D', 'disponible'),
    ('I', 'indisponible'),
    ('PT', 'presque terminé'),
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    stock = models.CharField(choices=AVAILIBILITY_CHOICES, max_length=2)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to='produits/%Y/%m/%d')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            'slug': self.slug
        })

class Photo(models.Model):
    """
    Les photos permettent d'illustrer les produits afin d'inciter l'internaute à les acheter.
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='produits/%Y/%m/%d')


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a BillingAddress
    (Failed Checkout)
    3. Payment
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    country = CountryField(multiple=False, default='United States')
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'BillingAddresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"

