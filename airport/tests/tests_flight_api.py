from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Country, City, Airport, Route, Flight, Crew
from airport.serializers import FlightListSerializer
from airport.tests.tests_airplane_api import (
    detail_flight_url,
    sample_airplane,
)


FLIGHT_URL = reverse("airport:flight-list")


def sample_city(**params):
    country = Country.objects.create(name="Country")

    defaults = {"name": "City", "country": country}
    defaults.update(params)

    return City.objects.create(**defaults)


def sample_airport(**params):
    city = sample_city(**params)

    defaults = {"name": "Airport", "closest_big_city": city}
    defaults.update(params)

    return Airport.objects.create(**defaults)


def sample_route(**params):
    source = sample_airport(name="Source Airport")
    destination = sample_airport(name="Destination Airport")

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 1000,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_flight(**params):
    airplane = sample_airplane()
    route = sample_route()
    crew = Crew.objects.create(first_name="First_name", last_name="Last_name")

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2024-08-24 08:15",
        "arrival_time": "2024-08-24 08:16",
    }
    defaults.update(params)

    flight = Flight.objects.create(**defaults)
    flight.tickets_available = 120

    return flight


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_flight_details(self):
        flight = sample_flight()
        url = detail_flight_url(flight.id)

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_by_airplanes(self):
        airplane_1 = sample_airplane()
        airplane_2 = sample_airplane(rows=200)
        airplane_3 = sample_airplane(rows=300)

        flight_1 = sample_flight(airplane=airplane_1)
        flight_2 = sample_flight(airplane=airplane_2)
        flight_3 = sample_flight(airplane=airplane_3)

        res = self.client.get(
            FLIGHT_URL, {
                "airplanes": f"{flight_1.id},{flight_2.id}"
            }
        )

        res_ids = [x["id"] for x in res.data["results"]]

        self.assertIn(flight_1.id, res_ids)
        self.assertIn(flight_2.id, res_ids)
        self.assertNotIn(flight_3, res_ids)

    def test_filter_by_sources(self):
        source_1 = sample_route()
        source_2 = sample_route(source=sample_airport(name="London"))
        source_3 = sample_route(source=sample_airport(name="Paris"))

        flight_1 = sample_flight(route=source_1)
        flight_2 = sample_flight(route=source_2)
        flight_3 = sample_flight(route=source_3)

        res = self.client.get(
            FLIGHT_URL, {
                "routers": f"{source_1.id},{source_2.id}"
            }
        )

        serializer_1 = FlightListSerializer(flight_1)
        serializer_2 = FlightListSerializer(flight_2)
        serializer_3 = FlightListSerializer(flight_3)

        self.assertIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_2.data, res.data["results"])
        self.assertIn(serializer_3.data, res.data["results"])

    def test_filter_by_dates(self):
        flight_1 = sample_flight()
        flight_2 = sample_flight(departure_time="2024-08-25 08:16")
        flight_3 = sample_flight(departure_time="2024-08-26 08:16")

        res = self.client.get(
            FLIGHT_URL, {
                "departure_time": "2024-08-25"
            }
        )

        res_ids = [x["id"] for x in res.data["results"]]

        self.assertNotIn(flight_1.id, res_ids)
        self.assertIn(flight_2.id, res_ids)
        self.assertNotIn(flight_3.id, res_ids)

    def test_create_flight_forbidden(self):
        route = sample_route()
        airplane = sample_airplane()

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-11-18T14:00:00+02:00",
            "arrival_time": "2023-11-18T19:00:00+02:00",
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test", password="adminpassword", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_flight(self):
        route = sample_route()
        airplane = sample_airplane()
        crew = Crew.objects.create(
            first_name="First_name",
            last_name="Last_name",
        )

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": "2023-11-18T14:00:00+02:00",
            "arrival_time": "2023-11-18T19:00:00+02:00",
            "crew": crew.id,
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
