from django.urls import path
from cars.views import (CarListView, CarDetailView, CarCreateView, CarUpdateView,
                        CarDeleteView, CarRentView, MyRentalsView, ReturnCarView, MyCarsView)

app_name = "cars"

urlpatterns = [
    path("", CarListView.as_view(), name="car_list"),
    path("car/my_cars", MyCarsView.as_view(), name="my_cars"),
    path("car/<int:pk>/", CarDetailView.as_view(), name="car_detail"),
    path("car/add/", CarCreateView.as_view(), name="car_add"),
    path("car/<int:pk>/edit/", CarUpdateView.as_view(), name="car_edit"),
    path("car/<int:pk>/delete/", CarDeleteView.as_view(), name="car_delete"),
    path("car/<int:pk>/rent/", CarRentView.as_view(), name="car_rent"),
    path("my-rentals/", MyRentalsView.as_view(), name="my_rentals"),
    path("rental/<int:pk>/return/", ReturnCarView.as_view(), name="return_car"),
]