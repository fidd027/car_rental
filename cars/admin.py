from django.contrib import admin

from cars.models import Car, CarType, CarRental

# admin.site.register([Car, CarType])


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('car_make', 'car_type', 'model_year', 'registration_number', 'is_available')
    actions = ('make_product_available', 'make_product_unavailable')

    @admin.action(description="<Make product available>")
    def make_product_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description="<Make product unavailable>")
    def make_product_unavailable(self, request, queryset):
        queryset.update(is_available=False)



@admin.register(CarType)
class CarTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
