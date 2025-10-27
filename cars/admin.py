from django.contrib import admin

from cars.models import Car, CarType, CarRental

admin.site.register([Car, CarType])
# @admin.register(Car)
# class CarAdmin(admin.ModelAdmin):
#     list_display = ('id', 'number', 'type')
#
#
# @admin.register(CarType)
# class CarTypeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
