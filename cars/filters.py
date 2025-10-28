import django_filters
from .models import Car


class CarFilter(django_filters.FilterSet):
    car_make = django_filters.ChoiceFilter(
        choices=Car.CAR_MAKE_CHOICES,
        label="Make"
    )

    transmission = django_filters.ChoiceFilter(
        choices=Car.TRANSMISSION_CHOICES,
        label="Transmission"
    )

    car_capacity = django_filters.ChoiceFilter(
        choices=Car.CAPACITY_CHOICES,
        label="Seats"
    )


    model_year = django_filters.RangeFilter(label='Model Year(Range)')

    class Meta:
        model = Car
        fields = ["car_make", "car_type", "transmission", "car_capacity", "model_year", "is_available"]
