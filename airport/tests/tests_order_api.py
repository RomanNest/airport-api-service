from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Order
from airport.serializers import OrderListSerializer
from airport.tests.tests_flight_api import sample_flight


ORDER_URL = reverse("airport:order-list")


class UnauthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_to_get_order(self):
        res = self.client.get(ORDER_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_to_create(self):
        user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )

        payload = {"user": user.id}

        res = self.client.post(ORDER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_orders(self):
        Order.objects.create(user=self.user)
        Order.objects.create(user=self.user)

        res = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_order(self):
        order = Order.objects.create(user=self.user)

        payload = {
            "tickets": [
                {
                    "row": 1,
                    "seat": 1,
                    "flight": sample_flight().id,
                    "order": order.id,
                }
            ],
        }

        res = self.client.post(
            ORDER_URL, data=payload, format="json"
        )
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

