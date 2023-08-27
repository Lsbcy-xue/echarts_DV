from django.contrib import admin
from .models import RegionData, Gini, IncomeData

# Register your models here.

admin.site.register(RegionData)
admin.site.register(Gini)
admin.site.register(IncomeData)