from datetime import datetime

from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
    AirplaneImageSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()

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


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        elif self.action == "retrieve":
            return AirplaneDetailSerializer
        elif self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects
    permission_classes = (IsAuthenticated,)

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
    queryset = (
        Flight.objects.all()
        .select_related(
            "route__source", "route__destination", "airplane__airplane_type"
        )
        .prefetch_related("crew")
    )

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
                tickets_available=F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
              name="airplanes",
              type={"type": "list", "items": {"type": "number"}},
              description="Filter by airplane id (ex. ?airplanes=2,3)",
            ),
            OpenApiParameter(
                name="source",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by source id (ex. ?source=2,3)",
            ),
            OpenApiParameter(
                name="destination",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by destination id (ex. ?destination=2,3)",
            ),
            OpenApiParameter(
                name="data",
                type=OpenApiTypes.DATE,
                description="Filter by flight date (ex. ?date=2025-08-24)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()

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
