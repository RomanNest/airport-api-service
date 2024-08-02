from rest_framework import serializers
from airport.models import (
    Airport,
    Route,
    Country,
    City,
    Crew,
    Flight,
    Ticket,
    Order,
    AirplaneType,
    Airplane,
)


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id", "name", "country")



