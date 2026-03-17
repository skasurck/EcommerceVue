from decimal import Decimal
from unittest.mock import patch
from django.urls import reverse
from django.test import SimpleTestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from productos.models import Categoria, Producto, PrecioEscalonado, ProductClassificationFeedback
from productos.ai import _normalize_labels, classify_text, MAIN_CATEGORIES
from productos.learning import get_feedback_model, predict_with_feedback


class PrecioEscalonadoAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="admin", password="pass1234")
        self.user.perfil.rol = "admin"
        self.user.perfil.save()
        self.client.force_authenticate(self.user)

        self.producto = Producto.objects.create(
            nombre="Prod",
            precio_normal=100,
            stock=10,
        )
        self.tier = PrecioEscalonado.objects.create(
            producto=self.producto, cantidad_minima=5, precio_unitario=90
        )

    def test_actualizar_precios_escalonados(self):
        url = reverse("producto-detail", args=[self.producto.id])
        payload = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": True,
            "estado_inventario": "en_existencia",
            "visibilidad": True,
            "estado": "borrador",
            "precios_escalonados": [
                {"id": self.tier.id, "cantidad_minima": 5, "precio_unitario": "95"},
                {"cantidad_minima": 20, "precio_unitario": "80"},
            ],
        }
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, 200)
        tiers = list(
            PrecioEscalonado.objects.filter(producto=self.producto)
            .order_by("cantidad_minima")
            .values_list("cantidad_minima", "precio_unitario")
        )
        self.assertEqual(tiers, [(5, Decimal("95")), (20, Decimal("80"))])

    def test_actualizar_precios_escalonados_json_string(self):
        url = reverse("producto-detail", args=[self.producto.id])
        import json
        data = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": "true",
            "estado_inventario": "en_existencia",
            "visibilidad": "true",
            "estado": "borrador",
            "precios_escalonados": json.dumps([
                {"id": self.tier.id, "cantidad_minima": 5, "precio_unitario": "95"},
                {"cantidad_minima": 20, "precio_unitario": "80"},
            ]),
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        tiers = list(
            PrecioEscalonado.objects.filter(producto=self.producto)
            .order_by("cantidad_minima")
            .values_list("cantidad_minima", "precio_unitario")
        )
        self.assertEqual(tiers, [(5, Decimal("95")), (20, Decimal("80"))])

    def test_actualizar_precios_escalonados_multipart(self):
        url = reverse("producto-detail", args=[self.producto.id])
        data = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": "true",
            "estado_inventario": "en_existencia",
            "visibilidad": "true",
            "estado": "borrador",
            "precios_escalonados[0][id]": str(self.tier.id),
            "precios_escalonados[0][cantidad_minima]": "5",
            "precios_escalonados[0][precio_unitario]": "95",
            "precios_escalonados[1][cantidad_minima]": "20",
            "precios_escalonados[1][precio_unitario]": "80",
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        tiers = list(
            PrecioEscalonado.objects.filter(producto=self.producto)
            .order_by("cantidad_minima")
            .values_list("cantidad_minima", "precio_unitario")
        )
        self.assertEqual(tiers, [(5, Decimal("95")), (20, Decimal("80"))])

    def test_update_con_valores_null(self):
        """Acepta cadenas 'null' o vacías en campos opcionales."""
        url = reverse("producto-detail", args=[self.producto.id])
        data = {
            "nombre": "Prod",
            "precio_normal": "100",
            "stock": 10,
            "disponible": "true",
            "estado_inventario": "en_existencia",
            "visibilidad": "true",
            "estado": "borrador",
            "categoria": "null",
            "marca": "",
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.assertIsNone(self.producto.categoria)
        self.assertIsNone(self.producto.marca)


class ProductAINormalizationTests(SimpleTestCase):
    def test_proyector_prioriza_ruta_de_proyeccion(self):
        text = "PROYECTOR EPSON POWERLITE W49 3800 LUMENS HDMI USB VGA"
        result = _normalize_labels(
            text=text,
            main_label="Cómputo (Hardware)",
            sub_label="Cómputo (Hardware) > Adaptadores > RJ-45",
            main_score=0.55,
            sub_score=0.50,
        )

        self.assertEqual(result.main, "Audio y Video")
        self.assertIn("Proyectores", result.sub or "")

    def test_ssd_externo_prioriza_categoria_ssd_externos(self):
        text = "SSD EXTERNO LENOVO LP100 1TB USB 3.2 USB-C 455MB/S GRIS"
        result = _normalize_labels(
            text=text,
            main_label="Energía",
            sub_label="Energía > Energía Computo > Fuentes de Poder para PC's",
            main_score=0.61,
            sub_score=0.55,
        )

        self.assertEqual(result.main, "Cómputo (Hardware)")
        self.assertEqual(
            result.sub,
            "Cómputo (Hardware) > Discos Duros / SSD / NAS > SSD's Externos",
        )

    def test_ssd_generico_sin_externo_permanece_en_ssd(self):
        text = "SSD NVME M.2 PCIe 1TB para laptop"
        result = _normalize_labels(
            text=text,
            main_label="Energía",
            sub_label="Energía > Energía Computo > Fuentes de Poder para PC's",
            main_score=0.58,
            sub_score=0.49,
        )

        self.assertEqual(result.main, "Cómputo (Hardware)")
        self.assertEqual(
            result.sub,
            "Cómputo (Hardware) > Discos Duros / SSD / NAS > SSD",
        )


class ProductAIClassificationDecisionTests(SimpleTestCase):
    @patch("productos.ai.get_image_pipeline")
    @patch("productos.ai.get_pipeline")
    def test_classify_text_combina_senal_de_imagen(self, mock_get_pipeline, mock_get_image_pipeline):
        class FakeTextClassifier:
            def __call__(self, text, candidate_labels, multi_label=False, hypothesis_template=None):
                labels = list(candidate_labels)
                if labels == MAIN_CATEGORIES:
                    return {
                        "labels": ["Cómputo (Hardware)", "Audio y Video", "Energía"],
                        "scores": [0.52, 0.48, 0.10],
                    }

                if any(("Proyectores" in label and "Proyecci" in label) for label in labels):
                    proy_label = next(label for label in labels if "Proyectores" in label and "Proyecci" in label)
                    other = next(label for label in labels if label != proy_label)
                    return {"labels": [proy_label, other], "scores": [0.80, 0.20]}

                if any("Adaptadores" in label for label in labels):
                    adapt_label = next(label for label in labels if "Adaptadores" in label)
                    other = next(label for label in labels if label != adapt_label)
                    return {"labels": [adapt_label, other], "scores": [0.78, 0.22]}

                return {"labels": labels[:1], "scores": [0.5]}

        class FakeImageClassifier:
            def __call__(self, image, candidate_labels):
                audio_prompt = next(label for label in candidate_labels if "projectors" in label)
                hardware_prompt = next(label for label in candidate_labels if "computer hardware" in label)
                return [
                    {"label": audio_prompt, "score": 0.95},
                    {"label": hardware_prompt, "score": 0.02},
                ]

        mock_get_pipeline.return_value = FakeTextClassifier()
        mock_get_image_pipeline.return_value = FakeImageClassifier()

        result = classify_text("EQUIPO DE PRESENTACION 4000 LUMENS HDMI", image=object())
        self.assertEqual(result.main, "Audio y Video")

    @patch("productos.ai.get_pipeline")
    def test_classify_text_prefiere_proyector_sobre_keyword_usb(self, mock_get_pipeline):
        class FakeClassifier:
            def __call__(self, text, candidate_labels, multi_label=False, hypothesis_template=None):
                labels = list(candidate_labels)
                if labels == MAIN_CATEGORIES:
                    return {
                        "labels": ["Cómputo (Hardware)", "Audio y Video", "Energía"],
                        "scores": [0.44, 0.41, 0.15],
                    }

                if any("Memorias USB" in label for label in labels):
                    usb_label = next(label for label in labels if "Memorias USB" in label)
                    other = next(label for label in labels if label != usb_label)
                    return {"labels": [usb_label, other], "scores": [0.68, 0.32]}

                if any(("Proyectores" in label and "Proyecci" in label) for label in labels):
                    proy_label = next(label for label in labels if "Proyectores" in label and "Proyecci" in label)
                    other = next(label for label in labels if label != proy_label)
                    return {"labels": [proy_label, other], "scores": [0.83, 0.17]}

                return {"labels": labels[:1], "scores": [0.5]}

        mock_get_pipeline.return_value = FakeClassifier()

        result = classify_text("PROYECTOR EPSON POWERLITE W49 3800 LUMENS HDMI USB VGA")
        self.assertEqual(result.main, "Audio y Video")
        self.assertIn("Proyectores", result.sub or "")


class ProductManualFeedbackCaptureTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="admin_feedback", password="pass1234")
        self.user.perfil.rol = "admin"
        self.user.perfil.save()
        self.client.force_authenticate(self.user)

        self.root = Categoria.objects.create(nombre="Impresión y Copiado")
        self.child = Categoria.objects.create(nombre="Impresoras y Multifuncionales", parent=self.root)
        self.leaf = Categoria.objects.create(nombre="Multifuncionales", parent=self.child)

        self.product = Producto.objects.create(
            nombre="MULTIFUNCIONAL HP LASER M236",
            descripcion_corta="impresora multifuncional wifi",
            precio_normal=1200,
            stock=4,
        )

    def test_apply_category_registra_feedback_manual(self):
        url = reverse("producto-apply-category", args=[self.product.id])
        response = self.client.post(
            url,
            {"category_ids": [self.root.id, self.child.id, self.leaf.id]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        feedback = ProductClassificationFeedback.objects.filter(producto=self.product).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.source, "manual_single")
        self.assertEqual(feedback.target_main, "Impresión y Copiado")
        self.assertEqual(
            feedback.target_sub,
            "Impresión y Copiado > Impresoras y Multifuncionales > Multifuncionales",
        )

    def test_bulk_apply_category_registra_feedback_manual(self):
        other = Producto.objects.create(
            nombre="MULTIFUNCIONAL HP SMART TANK",
            descripcion_corta="multifuncional tinta color",
            precio_normal=1300,
            stock=2,
        )
        url = reverse("producto-bulk-apply-category")
        response = self.client.post(
            url,
            {
                "products": [
                    {"product_id": self.product.id, "category_ids": [self.root.id, self.child.id, self.leaf.id]},
                    {"product_id": other.id, "category_ids": [self.root.id, self.child.id, self.leaf.id]},
                ]
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ProductClassificationFeedback.objects.filter(source="manual_bulk").count(),
            2,
        )


class ProductFeedbackLearningTests(APITestCase):
    def test_predict_with_feedback_usa_correcciones_guardadas(self):
        for _ in range(25):
            ProductClassificationFeedback.objects.create(
                input_text="multifuncional hp laser wifi impresion escaner",
                target_main="Impresión y Copiado",
                target_sub="Impresión y Copiado > Impresoras y Multifuncionales > Multifuncionales",
                source="manual_single",
            )

        model = get_feedback_model(force_refresh=True)
        self.assertIsNotNone(model)

        prediction = predict_with_feedback(
            "equipo multifuncional laser hp con escaner y wifi",
            model=model,
        )
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.main, "Impresión y Copiado")
        self.assertIn("Multifuncionales", prediction.sub)


class ProductLearningStatsAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.super_admin = User.objects.create_user(username="super_stats", password="pass1234")
        self.super_admin.perfil.rol = "super_admin"
        self.super_admin.perfil.save()

        self.admin = User.objects.create_user(username="admin_stats", password="pass1234")
        self.admin.perfil.rol = "admin"
        self.admin.perfil.save()

        self.product = Producto.objects.create(
            nombre="IMPRESORA HP",
            descripcion_corta="impresora laser",
            precio_normal=1500,
            stock=3,
        )
        ProductClassificationFeedback.objects.create(
            producto=self.product,
            input_text="impresora hp laser wifi",
            target_main="Impresión y Copiado",
            target_sub="Impresión y Copiado > Impresoras y Multifuncionales > Impresoras",
            source="manual_single",
        )

    def test_learning_stats_disponible_para_super_admin(self):
        self.client.force_authenticate(self.super_admin)
        url = reverse("ai-learning-stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("summary", response.data)
        self.assertIn("model", response.data)
        self.assertIn("by_source", response.data)
        self.assertIn("top_subcategories", response.data)
        self.assertEqual(response.data["summary"]["total_feedback"], 1)

    def test_learning_stats_denegado_para_admin(self):
        self.client.force_authenticate(self.admin)
        url = reverse("ai-learning-stats")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

