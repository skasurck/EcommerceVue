from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from pedidos.models import Direccion
from .models import Perfil


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "email")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user


class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ["telefono", "empresa", "rol"]
        read_only_fields = ["rol"]


class UserProfileSerializer(serializers.ModelSerializer):
    perfil = PerfilSerializer(required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "perfil"]
        read_only_fields = ["username"]

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop("perfil", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        perfil, _ = Perfil.objects.get_or_create(user=instance)
        for attr, value in perfil_data.items():
            setattr(perfil, attr, value)
        perfil.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña anterior incorrecta")
        return value

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PerfilAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = ["telefono", "empresa", "rol"]


class DireccionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = [
            "id",
            "user",
            "nombre",
            "apellidos",
            "email",
            "nombre_empresa",
            "calle",
            "numero_exterior",
            "numero_interior",
            "colonia",
            "ciudad",
            "pais",
            "estado",
            "codigo_postal",
            "telefono",
            "referencias",
            "predeterminada",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "user"]

    def create(self, validated_data):
        user = self.context["user"]
        direccion = Direccion.objects.create(user=user, **validated_data)
        if validated_data.get("predeterminada") or not Direccion.objects.filter(user=user, predeterminada=True).exclude(pk=direccion.pk).exists():
            Direccion.objects.filter(user=user).exclude(pk=direccion.pk).update(predeterminada=False)
            direccion.predeterminada = True
            direccion.save(update_fields=["predeterminada"])
        return direccion

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if validated_data.get("predeterminada"):
            Direccion.objects.filter(user=instance.user).exclude(pk=instance.pk).update(predeterminada=False)
        elif not Direccion.objects.filter(user=instance.user, predeterminada=True).exists():
            instance.predeterminada = True
            instance.save(update_fields=["predeterminada"])
        return instance


class UserAdminListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    rol = serializers.CharField(source="perfil.rol", read_only=True)
    estado_2fa = serializers.SerializerMethodField()
    ultimo_acceso = serializers.DateTimeField(source="last_login", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nombre_completo",
            "email",
            "rol",
            "estado_2fa",
            "ultimo_acceso",
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_estado_2fa(self, obj):
        return False


class UserAdminDetailSerializer(serializers.ModelSerializer):
    perfil = PerfilAdminSerializer()
    direccion_predeterminada = DireccionAdminSerializer(required=False)
    direcciones = DireccionAdminSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "perfil",
            "direccion_predeterminada",
            "direcciones",
        ]
        read_only_fields = ["id", "username"]

    def validate_email(self, value):
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(pk=user_id).filter(email=value).exists():
            raise serializers.ValidationError("Email ya registrado")
        return value

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop("perfil", {})
        direccion_data = validated_data.pop("direccion_predeterminada", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        perfil, _ = Perfil.objects.get_or_create(user=instance)
        for attr, value in perfil_data.items():
            setattr(perfil, attr, value)
        perfil.save()

        if direccion_data is not None:
            default = instance.direcciones.filter(predeterminada=True).first()
            if default:
                serializer = DireccionAdminSerializer(default, data=direccion_data, partial=True, context={"user": instance})
            else:
                serializer = DireccionAdminSerializer(data=direccion_data, context={"user": instance})
            serializer.is_valid(raise_exception=True)
            serializer.save(predeterminada=True)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        default = instance.direcciones.filter(predeterminada=True).first()
        data["direccion_predeterminada"] = DireccionAdminSerializer(default).data if default else None
        data["direcciones"] = DireccionAdminSerializer(instance.direcciones.all(), many=True).data
        return data
