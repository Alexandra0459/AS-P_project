from django.contrib import admin
from .models import ClinicManager, Dispatcher, Distance, Location, MedicineSupply, Order, User

# Register your models here.
admin.site.register(ClinicManager)
admin.site.register(Dispatcher)
admin.site.register(Distance)
admin.site.register(Location)
admin.site.register(MedicineSupply)
admin.site.register(Order)
admin.site.register(User)