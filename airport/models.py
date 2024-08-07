from django.db import models

from airport_api_service import settings


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports",
    )

    def __str__(self):
        return f"{self.name} - {self.closest_big_city}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routers"
    )
    distance = models.IntegerField(default=0)

    def __str__(self):
        return (
            f"{self.source.name} - {self.destination.name} "
            f"({self.distance} km.)"
        )


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()


class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_rows = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes",
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self):
        return self.rows * self.seats_in_rows

    def __str__(self):
        return self.name


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return (
            f"{self.route.source} - {self.route.distance}:"
            f"{self.departure_time} -> {self.arrival_time}"
        )


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        unique_together = ["flight", "row", "seat"]

    def __str__(self):
        return (
            f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order: {self.id} created: {self.created_at}"
