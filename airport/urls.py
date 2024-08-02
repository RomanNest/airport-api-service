from django.urls import path, include
from rest_framework import routers

from airport.views import CountryViewSet

app_name = "airport"

router = routers.DefaultRouter()
router.register("countries", CountryViewSet)

urlpatterns = [path("", include(router.urls))]
