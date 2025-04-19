from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import HealthCheckSerializer


@extend_schema(responses=HealthCheckSerializer, tags=["Health"])
class HealthCheckView(APIView):
    def get(self, _):
        """
        Returns a simple JSON response for health check
        """
        serializer = HealthCheckSerializer({"status": "ok"})
        return Response(serializer.data)
