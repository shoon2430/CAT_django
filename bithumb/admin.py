from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(ProgramUser)
admin.site.register(TradeHistory)
admin.site.register(TradeScheduler)
admin.site.register(Wallet)
