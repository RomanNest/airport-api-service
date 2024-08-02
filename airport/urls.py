from django.urls import path, include
from rest_framework import routers

from airport.views import CountryViewSet, CityViewSet

app_name = "airport"

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)
router.register("cities", CityViewSet)

urlpatterns = [path("", include(router.urls))]
