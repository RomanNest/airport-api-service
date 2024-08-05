from django.urls import path, include
from rest_framework import routers

from airport.views import (
    CountryViewSet,
    CityViewSet,
    AirportViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    OrderViewSet,
    TicketViewSet,
)

app_name = "airport"

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)
router.register("airports", AirportViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)


urlpatterns = [path("", include(router.urls))]
