
from django.db import models
from django.conf import settings
from django.core.exceptions import PermissionDenied
from datetime import datetime
from django.utils import timezone


class CarType(models.Model):
    """Model representing the type or category of a car."""
    name = models.CharField(max_length=100, unique=True)


    class Meta:
        verbose_name = "Car Type"
        verbose_name_plural = "Car Types"
        ordering = ['name']

    def __str__(self):
        return self.name


class Car(models.Model):


    TRANSMISSION_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('CVT', 'cvt'),
    ]

    CAPACITY_CHOICES = [
        ('2', 2),
        ('4', 4),
        ('5', 5),
        ('7', 7),
        ('8 and more', 8)
    ]

    LOCATION_CHOICES = [
        ('Tbilisi', 'Tbilisi'),
        ('Kutaisi', 'Kutaisi'),
        ('Batumi', 'Batumi'),
        ('Rustavi', 'Rustavi'),
        ('Dmanisi', 'Dmanisi'),

    ]

    CAR_MAKE_CHOICES = [
        ('toyota', 'Toyota'),
        ('honda', 'Honda'),
        ('ford', 'Ford'),
        ('chevrolet', 'Chevrolet'),
        ('Nissan', 'nissan'),
        ('volkswagen', 'Volkswagen'),
        ('bmw', 'BMW'),
        ('mercedes', 'Mercedes-Benz'),
        ('Audi', 'Audi'),
        ('hyundai', 'Hyundai'),
        ('kia', 'Kia'),
        ('mazda', 'Mazda'),
        ('subaru', 'Subaru'),
        ('tesla', 'Tesla'),
        ('jeep', 'Jeep'),
        ('land_rover', 'Land Rover'),
        ('volvo', 'Volvo'),
        ('Porsche', 'porsche'),
        ('Lexus', 'lexus'),
        ('rolls-royce', 'Rolls-Royce'),
    ]

    CURRENT_YEAR = datetime.now().year
    YEAR_CHOICES = [(year, str(year)) for year in range(1990, CURRENT_YEAR + 1)]

    car_type = models.ForeignKey(CarType, on_delete=models.SET_NULL, null=True, related_name="cars")
    car_make = models.CharField(choices=CAR_MAKE_CHOICES, max_length=20, )
    car_model = models.CharField(max_length=100)
    model_year = models.PositiveIntegerField(choices=YEAR_CHOICES, default=CURRENT_YEAR)
    registration_number = models.CharField(max_length=50, unique=True)
    car_capacity = models.CharField(choices=CAPACITY_CHOICES, default='5', max_length=15)
    transmission = models.CharField(choices=TRANSMISSION_CHOICES, max_length=10, default='Automatic')
    location = models.CharField(choices=LOCATION_CHOICES, max_length=10, default='Tbilisi')
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='car_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='car_images/', blank=True, null=True)
    description = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cars_added"
    )

    class Meta:
        db_table = "cars"
        ordering = ['-date_added']
        verbose_name_plural = "Cars"

    def __str__(self):
        return f"{self.car_make} {self.car_model} ({self.model_year})"

    def delete(self, *args, **kwargs):
        """Only allow the user who added the car to delete it."""
        user = kwargs.pop('user', None)
        if user is not None and user != self.added_by:
            raise PermissionDenied("You can only delete cars that you added.")
        super().delete(*args, **kwargs)


class CarRental(models.Model):
    """Model representing a car rental transaction."""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="rentals")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rental"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    rented_on = models.DateTimeField(auto_now_add=True)
    returned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-rented_on']
        verbose_name = "Car Rental"
        verbose_name_plural = "Car Rentals"

    def __str__(self):
        # show phone number for your custom user
        return f"{self.car} rented by {self.user.phone_number}"

    def save(self, *args, **kwargs):
        """Automatically calculate total price and mark car as unavailable."""
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days or 1
            self.total_price = days * self.car.price_per_day
        super().save(*args, **kwargs)

        # Mark car as unavailable if currently rented
        if not self.returned:
            self.car.is_available = False
            self.car.save()

    def mark_returned(self):
        """Mark car as returned and make it available again."""
        self.returned = True
        self.save()
        self.car.is_available = True
        self.car.save()
