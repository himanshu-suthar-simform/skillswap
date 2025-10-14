from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def healthcheck(request):
    """
    A simple health check endpoint to verify that the application is running.
    """
    return Response({"status": "ok"}, status=status.HTTP_200_OK)
