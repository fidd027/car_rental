from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from datetime import datetime

from .forms import CarForm
from .models import Car, CarType, CarRental

from django_filters.views import FilterView
from .filters import CarFilter
from .models import Car
from django.contrib import messages
from django.core.paginator import Paginator


 # CAR VIEWS

class CarListView(FilterView):

    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"
    filterset_class = CarFilter
    paginate_by = 6
    select_related = True


    # ამის ჩართვით მომხმარებლებს მხოლოდ იმ მანქანებს უჩვენებს, რომლებიც გაქირავებულები არ არიან
    # def get_queryset(self):
    #     # Show only available cars by default
    #     queryset = super().get_queryset()
    #     return Car.objects.filter(is_available=True).select_related("car_type", "added_by")

class MyCarsView(FilterView):

    model = Car
    template_name = "my_cars.html"
    context_object_name = "cars"
    filterset_class = CarFilter
    select_related = True

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset.filter(
            added_by=self.request.user
        ).select_related("car_type", "added_by")


class CarDetailView(DetailView):

    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"


class CarCreateView(LoginRequiredMixin, CreateView):

    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("cars:car_list")


    def form_valid(self, form):

        form.instance.added_by = self.request.user
        return super().form_valid(form)


class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow the owner to edit their car details."""
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("cars:car_detail")
    pk_url_kwarg = 'pk'

    def test_func(self):
        car = self.get_object()
        return self.request.user == car.added_by

    def get_success_url(self):
        return reverse('cars:car_detail', kwargs={'pk': self.object.pk})


class CarDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Car
    template_name = "car_confirm_delete.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy("cars:car_list")

    def test_func(self):
        car = self.get_object()
        return self.request.user == car.added_by




# ------------------ RENTAL VIEWS ------------------ #

class CarRentView(LoginRequiredMixin, View):

    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        start_date_str = request.POST.get("start_date")
        end_date_str = request.POST.get("end_date")

        # Validate rental period
        if not start_date_str or not end_date_str:
            return redirect("cars:car_detail", pk=car.pk)

        if self.request.user == car.added_by:
            messages.error(request, "You can't Rent your own car")
            return redirect("cars:car_detail", pk=car.pk)

        if not car.is_available:
            return redirect("cars:car_detail", pk=car.pk)

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:

            return redirect("cars:car_detail", pk=car.pk)

        if end_date <= start_date:

            return redirect("cars:car_detail", pk=car.pk)

        if not car.is_available:
            return redirect("cars:car_detail", pk=car.pk)

        # Create rental record
        CarRental.objects.create(
            car=car,
            user=request.user,
            start_date=start_date,
            end_date=end_date,
        )
        car.is_available = False
        car.save()

        return redirect("cars:my_rentals")


class MyRentalsView(LoginRequiredMixin, ListView):
    """Show all rentals made by the logged-in user."""
    model = CarRental
    template_name = "my_rentals.html"
    context_object_name = "rentals"

    def get_queryset(self):
        return CarRental.objects.filter(user=self.request.user).select_related("car")


class ReturnCarView(LoginRequiredMixin, View):
    """Mark a car as returned."""
    def post(self, request, pk):
        rental = get_object_or_404(CarRental, pk=pk, user=request.user)
        rental.mark_returned()
        return redirect("cars:my_rentals")
