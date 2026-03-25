# promotions/views.py
from rest_framework import generics, views, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.core.management import call_command
from io import StringIO

from .models import Cupon, PromotionSettings
from .serializers import CuponSerializer, PromotionSettingsSerializer, ValidarCuponSerializer

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


class CuponViewSet(viewsets.ModelViewSet):
    """CRUD de cupones (solo admin). Endpoint público para validar."""
    queryset = Cupon.objects.all().order_by('-id')
    serializer_class = CuponSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='validar')
    def validar(self, request):
        """POST /api/cupones/validar/  →  valida un código y devuelve el descuento calculado."""
        serializer = ValidarCuponSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        codigo = serializer.validated_data['codigo'].strip().upper()
        subtotal = serializer.validated_data['subtotal']

        try:
            cupon = Cupon.objects.get(codigo__iexact=codigo)
        except Cupon.DoesNotExist:
            return Response({'detail': 'Cupón no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        ok, mensaje = cupon.es_valido(subtotal)
        if not ok:
            return Response({'detail': mensaje}, status=status.HTTP_400_BAD_REQUEST)

        descuento = cupon.calcular_descuento(subtotal)
        return Response({
            'id': cupon.id,
            'codigo': cupon.codigo,
            'descripcion': cupon.descripcion,
            'tipo': cupon.tipo,
            'valor': str(cupon.valor),
            'descuento': str(descuento),
        }, status=status.HTTP_200_OK)