from datetime import datetime

from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from airport.models import (
    Country,
    City,
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Order,
    Flight,
    Route,
)
from airport.permissions import IsAdminAllOrIsAuthenticatedReadOnly
from airport.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    OrderSerializer,
    FlightSerializer,
    RouteSerializer,
    RoutListSerializer,
    RoutDetailSerializer,
    CityListSerializer,
    CityDetailSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderListSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return CityListSerializer
        if self.action == "retrieve":
            return CityDetailSerializer
        return CitySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        if self.action == "retrieve":
            return AirportDetailSerializer
        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__flight__airplane", "tickets__flight__route"
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all().select_related(
        "route__source",
        "route__destination",
        "airplane__airplane_type"
    ).prefetch_related("crew")
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(query_string):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in query_string.split(",")]

    def get_queryset(self):
        airplanes = self.request.query_params.get("airplanes")
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        date = self.request.query_params.get("departure_time")

        queryset = self.queryset

        if airplanes:
            airplanes_id = self._params_to_ints(airplanes)
            queryset = queryset.filter(airplane__id__in=airplanes_id)

        if source:
            source_id = self._params_to_ints(source)
            queryset = queryset.filter(route__source_id__in=source_id)

        if destination:
            destination_id = self._params_to_ints(destination)
            queryset = queryset.filter(route__destination__id__in=destination_id)

        if date:
            departure_date = datetime.strptime(date, "%Y-%m-%d")
            queryset = queryset.filter(
                departure_time__year=departure_date.year,
                departure_time__month=departure_date.month,
                departure_time__day=departure_date.day,
            )

        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (IsAdminAllOrIsAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RoutListSerializer
        elif self.action == "retrieve":
            return RoutDetailSerializer
        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("source", "destination")
        return queryset
