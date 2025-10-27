from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from .forms import CarForm
from .models import Car, CarType, CarRental


# ------------------ CAR VIEWS ------------------ #

class CarListView(ListView):
    """List all available cars."""
    model = Car
    template_name = "car_list.html"
    context_object_name = "cars"

    def get_queryset(self):
        # Show only available cars by default
        return Car.objects.filter(is_available=True).select_related("car_type", "added_by")


class CarDetailView(DetailView):
    """Display detailed info about a single car."""
    model = Car
    template_name = "car_detail.html"
    context_object_name = "car"


class CarCreateView(LoginRequiredMixin, CreateView):
    """Allow logged-in users to add new cars."""
    model = Car
    form_class = CarForm
    template_name = "car_form.html"
    success_url = reverse_lazy("cars:car_list")
    # login_url = reverse_lazy("login")

    # def form_valid(self, form):
    #     # assign current user as car owner
    #     form.instance.added_by = self.request.user
    #     return super().form_valid(form)


class CarUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Allow the owner to edit their car details."""
    model = Car
    fields = ["car_type", "car_make", "car_model", "model_year", "price_per_day", "description", ]
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

    # def delete(self, request, *args, **kwargs):
    #     car = self.get_object()
    #     if car.added_by != request.user:
    #         raise PermissionDenied("You can only delete cars you added.")
    #     return super().delete(request, *args, **kwargs)


# ------------------ RENTAL VIEWS ------------------ #

class CarRentView(LoginRequiredMixin, View):
    """Allow a user to rent a car if it’s available."""
    def post(self, request, pk):
        car = get_object_or_404(Car, pk=pk)
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        # Validate rental period
        if not start_date or not end_date:
            return redirect("car_detail", pk=car.pk)

        if not car.is_available:
            return redirect("car_detail", pk=car.pk)

        # Create rental record
        CarRental.objects.create(
            car=car,
            user=request.user,
            start_date=start_date,
            end_date=end_date,
        )
        car.is_available = False
        car.save()
        return redirect("my_rentals")


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
        return redirect("my_rentals")
