from django.contrib import admin
from .models import Wallet, Address, Transaction

# Register your models here.
admin.site.register(Wallet)
admin.site.register(Address)
admin.site.register(Transaction)