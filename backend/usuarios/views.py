from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserAdminListSerializer,
    UserAdminDetailSerializer,
    DireccionAdminSerializer,
)
from .models import Perfil
from pedidos.models import Direccion, Pedido
from carrito.services import sync_session_cart_with_user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        token = data.pop("access")
        data = {
            "token": token,
            "user": {
                "id": self.user.id,
                "nombre": self.user.first_name,
                "email": self.user.email,
                "rol": getattr(self.user.perfil, "rol", "")
            }
        }
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        response = Response(serializer.validated_data, status=status.HTTP_200_OK)
        if request.session is not None:
            sync_session_cart_with_user(request.session, serializer.user)
        return response


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Usuario creado"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        Perfil.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        Perfil.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Contraseña actualizada"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(never_cache, name='list')
@method_decorator(never_cache, name='retrieve')
class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('perfil')
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserAdminListSerializer
        return UserAdminDetailSerializer

    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        rol = request.query_params.get('rol')
        qs = self.queryset
        if search:
            qs = qs.filter(
                Q(username__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )
        if rol:
            qs = qs.filter(perfil__rol=rol)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        perfil = request.data.get('perfil', {})
        if (
            isinstance(perfil, dict)
            and perfil.get('rol') == 'super_admin'
            and getattr(user.perfil, 'rol', '') != 'super_admin'
        ):
            return Response(
                {"detail": "El rol super_admin no es asignable por este endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def bulk_set_role(self, request):
        ids = request.data.get('ids', [])
        rol = request.data.get('rol')
        if rol == 'super_admin':
            return Response(
                {"detail": "El rol super_admin no es asignable por este endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )
        actualizados = Perfil.objects.filter(user__id__in=ids).update(rol=rol)
        return Response({'actualizados': actualizados})

    @action(detail=True, methods=['post'])
    def reset_password_link(self, request, pk=None):
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get('new_password')
        # restriction: only a superadmin can change another superadmin's password
        perfil_target = getattr(user, 'perfil', None)
        is_target_superadmin = user.is_superuser or (
            perfil_target and getattr(perfil_target, 'rol', '') == 'super_admin'
        )
        perfil_request = getattr(request.user, 'perfil', None)
        is_request_superadmin = request.user.is_superuser or (
            perfil_request and getattr(perfil_request, 'rol', '') == 'super_admin'
        )
        if is_target_superadmin and not is_request_superadmin:
            return Response(
                {
                    'detail': 'Solo un superadmin puede cambiar la contraseña de otro superadmin.'
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if not new_password:
            return Response({'detail': 'new_password requerido'}, status=400)
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response(
                {'detail': getattr(e, 'messages', [str(e)])},
                status=400,
            )
        user.set_password(new_password)
        user.save()
        return Response({'status': 'ok'})

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser or getattr(user.perfil, 'rol', '') == 'super_admin':
            return Response(
                {"detail": "Prohibido eliminar superadmin"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get', 'post'], url_path='direcciones')
    def direcciones(self, request, pk=None):
        user = self.get_object()
        if request.method == 'GET':
            serializer = DireccionAdminSerializer(user.direcciones.all(), many=True)
            return Response(serializer.data)
        serializer = DireccionAdminSerializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'delete'], url_path='direcciones/(?P<dir_id>[^/.]+)')
    def direccion_detalle(self, request, pk=None, dir_id=None):
        user = self.get_object()
        try:
            direccion = user.direcciones.get(id=dir_id)
        except Direccion.DoesNotExist:
            return Response({'detail': 'No encontrado'}, status=404)
        if request.method == 'PATCH':
            serializer = DireccionAdminSerializer(direccion, data=request.data, partial=True, context={'user': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if direccion.predeterminada and user.direcciones.exclude(id=direccion.id).exists():
            return Response({'detail': 'Debe seleccionar otra dirección predeterminada antes de eliminar'}, status=400)
        direccion.delete()
        return Response(status=204)

    @action(detail=True, methods=['post'], url_path='direcciones/(?P<dir_id>[^/.]+)/set_default')
    def set_default(self, request, pk=None, dir_id=None):
        user = self.get_object()
        try:
            direccion = user.direcciones.get(id=dir_id)
        except Direccion.DoesNotExist:
            return Response({'detail': 'No encontrado'}, status=404)
        Direccion.objects.filter(user=user).update(predeterminada=False)
        direccion.predeterminada = True
        direccion.save(update_fields=['predeterminada'])
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'])
    def importar_direcciones(self, request, pk=None):
        user = self.get_object()
        pedidos_qs = Pedido.objects.filter(Q(user=user))
        if user.email:
            pedidos_qs = pedidos_qs | Pedido.objects.filter(user__isnull=True, direccion__email=user.email)
        direcciones = Direccion.objects.filter(id__in=pedidos_qs.values_list('direccion_id', flat=True)).distinct()
        importadas = 0
        ya_existian = 0
        for d in direcciones:
            if Direccion.objects.filter(
                user=user,
                calle=d.calle,
                numero_exterior=d.numero_exterior,
                colonia=d.colonia,
                ciudad=d.ciudad,
                estado=d.estado,
                codigo_postal=d.codigo_postal,
                pais=d.pais,
                telefono=d.telefono,
            ).exists():
                ya_existian += 1
                continue
            if d.user is None:
                d.user = user
                d.save(update_fields=['user'])
            else:
                d.pk = None
                d.user = user
                d.predeterminada = False
                d.save()
            importadas += 1
        if not user.direcciones.filter(predeterminada=True).exists():
            latest = user.direcciones.order_by('-created_at').first()
            if latest:
                Direccion.objects.filter(user=user).exclude(pk=latest.pk).update(predeterminada=False)
                latest.predeterminada = True
                latest.save(update_fields=['predeterminada'])
        return Response({'importadas': importadas, 'ya_existian': ya_existian})
