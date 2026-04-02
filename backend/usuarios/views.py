from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.password_validation import validate_password
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.conf import settings

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserAdminListSerializer,
    UserAdminDetailSerializer,
    DireccionAdminSerializer,
)
from django.core import signing
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
from io import BytesIO
import base64

from .models import Perfil
from pedidos.models import Direccion, Pedido
from carrito.services import sync_session_cart_with_user
from tienda.throttles import LoginRateThrottle, RegistroRateThrottle

_2FA_SALT = '2fa-challenge'
_2FA_MAX_AGE = 300  # 5 minutos


def _is_admin_user(user):
    try:
        return user.perfil.rol in ('admin', 'super_admin')
    except Exception:
        return user.is_staff or user.is_superuser


def _build_jwt_response(user, request=None):
    """Genera el payload JWT estándar para un usuario autenticado."""
    refresh = RefreshToken.for_user(user)
    try:
        rol = user.perfil.rol
    except Exception:
        rol = ''
    default_address = user.direcciones.filter(predeterminada=True).first()
    address_data = DireccionAdminSerializer(default_address).data if default_address else None
    if request and request.session:
        sync_session_cart_with_user(request.session, user)
    return {
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'nombre': user.first_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'rol': rol,
            'direccion_predeterminada': address_data,
        }
    }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        token = data.pop("access")
        try:
            rol = self.user.perfil.rol
        except Perfil.DoesNotExist:
            rol = ""
        default_address = self.user.direcciones.filter(predeterminada=True).first()
        default_address_data = DireccionAdminSerializer(default_address).data if default_address else None
        data = {
            "token": token,
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "nombre": self.user.first_name,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
                "rol": rol,
                "direccion_predeterminada": default_address_data,
            }
        }
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0])

        user = serializer.user

        # Si es admin/super_admin y tiene 2FA configurado → paso 2
        if _is_admin_user(user) and TOTPDevice.objects.filter(user=user, confirmed=True).exists():
            challenge = signing.dumps({'user_id': user.id}, salt=_2FA_SALT)
            return Response({'requires_2fa': True, 'challenge': challenge}, status=status.HTTP_200_OK)

        if request.session is not None:
            sync_session_cart_with_user(request.session, user)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegistroRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"mensaje": "Usuario creado"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        with transaction.atomic():
            Perfil.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def put(self, request):
        with transaction.atomic():
            Perfil.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(request.user, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfilePhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        foto = request.FILES.get('foto')
        if not foto:
            return Response({'detail': 'No se envió ninguna imagen.'}, status=status.HTTP_400_BAD_REQUEST)
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        if perfil.foto:
            perfil.foto.delete(save=False)
        perfil.foto = foto
        perfil.save(update_fields=['foto'])
        url = request.build_absolute_uri(perfil.foto.url)
        return Response({'foto_url': url})


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
    queryset = User.objects.all().select_related('perfil').order_by('id')
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


# ─── Vistas de 2FA para la API JWT ────────────────────────────────────────────

class Login2FAView(APIView):
    """Paso 2 del login: valida el código TOTP y devuelve el JWT."""
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        challenge = request.data.get('challenge', '')
        otp_code  = str(request.data.get('otp_code', '')).strip()

        if not challenge or not otp_code:
            return Response({'detail': 'challenge y otp_code son requeridos.'}, status=400)

        try:
            data = signing.loads(challenge, salt=_2FA_SALT, max_age=_2FA_MAX_AGE)
        except signing.SignatureExpired:
            return Response({'detail': 'El desafío expiró. Inicia sesión nuevamente.'}, status=400)
        except signing.BadSignature:
            return Response({'detail': 'Token inválido.'}, status=400)

        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=404)

        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        if not device or not device.verify_token(otp_code):
            return Response({'detail': 'Código incorrecto.'}, status=400)

        return Response(_build_jwt_response(user, request), status=200)


class Setup2FAView(APIView):
    """
    GET  → genera QR code para configurar la app de autenticador.
    POST → activa el dispositivo con el primer código.
    DELETE → desactiva 2FA.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _is_admin_user(request.user):
            return Response({'detail': 'Solo administradores pueden usar 2FA.'}, status=403)

        if TOTPDevice.objects.filter(user=request.user, confirmed=True).exists():
            return Response({'detail': 'El 2FA ya está activado.', 'activo': True})

        # Elimina dispositivos pendientes anteriores
        TOTPDevice.objects.filter(user=request.user, confirmed=False).delete()

        device = TOTPDevice.objects.create(
            user=request.user,
            name=f'Autenticador {request.user.username}',
            confirmed=False,
            tolerance=2,
        )

        # Genera QR como PNG en base64
        qr = qrcode.QRCode(version=1, box_size=6, border=4)
        qr.add_data(device.config_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = BytesIO()
        img.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        return Response({
            'activo': False,
            'qr_code': f'data:image/png;base64,{qr_b64}',
            'clave_manual': device.config_url,
        })

    def post(self, request):
        """Confirma el dispositivo con el primer código."""
        otp_code = str(request.data.get('otp_code', '')).strip()
        if not otp_code:
            return Response({'detail': 'otp_code es requerido.'}, status=400)

        device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
        if not device:
            return Response({'detail': 'No hay dispositivo pendiente. Solicita el QR primero.'}, status=400)

        if device.verify_token(otp_code):
            device.confirmed = True
            device.save()
            return Response({'detail': '2FA activado correctamente. ✓'})
        return Response({'detail': 'Código incorrecto. Verifica tu app.'}, status=400)

    def delete(self, request):
        """Desactiva 2FA del usuario."""
        otp_code = str(request.data.get('otp_code', '')).strip()
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        if not device:
            return Response({'detail': 'No tienes 2FA activo.'}, status=400)
        if not device.verify_token(otp_code):
            return Response({'detail': 'Código incorrecto.'}, status=400)
        TOTPDevice.objects.filter(user=request.user).delete()
        return Response({'detail': '2FA desactivado.'})


class Status2FAView(APIView):
    """Devuelve si el usuario actual tiene 2FA activo."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activo = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
        return Response({'activo': activo, 'es_admin': _is_admin_user(request.user)})


# ─── Recuperación de contraseña ───────────────────────────────────────────────

_RESET_SALT = 'password-reset'
_RESET_MAX_AGE = 1800  # 30 minutos


class PasswordResetRequestView(APIView):
    """Solicita restablecimiento de contraseña — envía email con token firmado."""
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        identifier = request.data.get('identifier', '').strip()
        if not identifier:
            return Response({'detail': 'Usuario o correo requerido.'}, status=400)

        user = (
            User.objects.filter(email__iexact=identifier).first()
            or User.objects.filter(username__iexact=identifier).first()
        )

        if user and user.email:
            token = signing.dumps({'user_id': user.id}, salt=_RESET_SALT)
            frontend_url = getattr(settings, 'FRONTEND_BASE_URL', 'http://localhost:5173')
            reset_url = f'{frontend_url}/reset-password?token={token}'
            send_mail(
                subject='Recuperación de contraseña — Mktska',
                message=(
                    f'Hola {user.username},\n\n'
                    f'Recibimos una solicitud para restablecer tu contraseña.\n\n'
                    f'Haz clic en el siguiente enlace (válido por 30 minutos):\n{reset_url}\n\n'
                    f'Si no solicitaste esto, ignora este correo.\n\n'
                    f'— El equipo de Mktska'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        # Respuesta genérica para evitar enumeración de usuarios
        return Response({'detail': 'Si el usuario existe, recibirás un correo con instrucciones.'})


class PasswordResetConfirmView(APIView):
    """Valida el token del email y actualiza la contraseña."""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token', '').strip()
        new_password = request.data.get('new_password', '')

        if not token or not new_password:
            return Response({'detail': 'token y new_password son requeridos.'}, status=400)

        try:
            data = signing.loads(token, salt=_RESET_SALT, max_age=_RESET_MAX_AGE)
        except signing.SignatureExpired:
            return Response({'detail': 'El enlace expiró. Solicita uno nuevo.'}, status=400)
        except signing.BadSignature:
            return Response({'detail': 'Token inválido.'}, status=400)

        try:
            user = User.objects.get(id=data['user_id'])
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=404)

        try:
            validate_password(new_password, user)
        except Exception as e:
            msgs = getattr(e, 'messages', [str(e)])
            return Response({'detail': msgs}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Contraseña actualizada. Ya puedes iniciar sesión.'})
