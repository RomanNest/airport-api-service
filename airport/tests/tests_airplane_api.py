import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airport.models import (
    Airplane,
    AirplaneType,
    Country,
    City,
    Airport,
    Route,
    Flight,
)
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
)

AIRPLANE_URL = reverse("airport:airplane-list")


def sample_airplane_type(**params) -> AirplaneType:
    defaults = {
        "name": "Type_test"
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params) -> Airplane:
    defaults = {
        "name": "Airplane_test",
        "rows": 20,
        "seats_in_row": 6,
        "airplane_type": sample_airplane_type(),
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


def image_upload_url(airplane_id):
    return reverse("airport:airplane-upload-image", args=(airplane_id,))


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=(airplane_id,))


def detail_flight_url(flight_id):
    return reverse("airport:flight-detail", args=(flight_id,))


class UnauthenticatedAirplaneApiTEsts(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTEsts(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_airplanes_list(self):
        sample_airplane()

        res = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()
        url = detail_url(airplane.id)

        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "test_airplane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTEsts(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test", password="adminpassword", is_staff=True
        )
        self.client.force_authenticate(user=self.user)

    def test_create_airplane(self):
        payload = {
            "name": "test_airplane",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": sample_airplane_type().id,
        }

        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], airplane.airplane_type.id)
            else:
                self.assertEqual(payload[key], getattr(airplane, key))


class AirplaneImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.test", password="testpassword",
        )
        self.client.force_authenticate(user=self.user)
        self.airplane = sample_airplane()
        self.country = Country.objects.create(name="Tests")
        self.city = City.objects.create(name="Tests", country=self.country)
        self.airport = Airport.objects.create(
            name="Airport", closest_big_city=self.city,
        )
        self.route = Route.objects.create(
            source=self.airport,
            destination=self.airport,
            distance=2000,
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2024-08-24 14:00:00",
            arrival_time="2024-08-24 16:00:00",
        )
        self.url = image_upload_url(self.airplane.id)

    def tearDown(self):
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self):
        """Test uploading an image to an airplane"""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (500, 500))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(self.url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image """
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_image_url_is_shown_on_airplane_detail(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (500, 500))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(self.url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (500, 500))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(self.url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPLANE_URL)

        self.assertIn("image", res.data["results"][0])

    def test_image_url_is_shown_on_flight_detail(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (500, 500))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(self.url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_flight_url(self.flight.id))

        self.assertIn("airplane_image", res.data)
