from django.test import Client, TestCase
from django.urls import reverse


class HealthCheckViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check(self):
        # Arrange
        url = reverse("health-check")

        # Act
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
