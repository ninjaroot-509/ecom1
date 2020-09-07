from django.contrib import admin

from .models import *
from .models import User
# from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User

# class ProfileInline(admin.TabularInline):
#     model = Profile


# class UserAdmin(DjangoUserAdmin):
#     inlines = [ ProfileInline,]

class ContactusAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject','date',)
    search_fields = ('name', 'email',)
    date_hierarchy = 'date'

admin.site.register(Contactus, ContactusAdmin)

admin.site.register(User)

class AproductAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author',
        'label')
    list_filter = ('label', 'created_on', 'author')
    search_fields = ('title', 'price')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['label', '-created_on']

class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'body')

admin.site.register(Message, MessageAdmin)
admin.site.register(Aproduct, AproductAdmin)

admin.site.register(Profile)

class PostAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'author',
		'status')
	list_filter = ('status', 'created_on', 'author')
	search_fields = ('title', 'body')
	prepopulated_fields = {'slug': ('title',)}
	raw_id_fields = ('author',)
	ordering = ['status', '-created_on']

class CommentAdmin(admin.ModelAdmin):
	list_display = ('name', 'post', 'created', 'active')
	list_filter = ('active', 'created', 'updated')
	search_fields = ('name', 'body')

admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)


############################Autres####################################


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['user',
                   'ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    inlines = [
        PhotoInline
    ]

admin.site.register(Item, ItemAdmin)

admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(BillingAddress, AddressAdmin)
