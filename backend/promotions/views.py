# promotions/views.py
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.core.management import call_command
from io import StringIO

from .models import PromotionSettings
from .serializers import PromotionSettingsSerializer

class PromotionSettingsView(generics.RetrieveUpdateAPIView):
    """
    API view to retrieve and update the global promotion settings.
    It operates on the singleton PromotionSettings object.
    """
    serializer_class = PromotionSettingsSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        # The load() method on the model ensures we always get the singleton instance.
        return PromotionSettings.load()

class RunDailyOffersCommandView(views.APIView):
    """
    API view to manually trigger the create_daily_offers management command.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        try:
            # Use StringIO to capture the output of the command
            out = StringIO()
            call_command('create_daily_offers', stdout=out)
            output = out.getvalue()
            return Response({"status": "success", "output": output}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)