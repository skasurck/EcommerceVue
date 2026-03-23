<template>
  <div class="max-w-3xl mx-auto px-4 py-10 prose prose-slate">
    <h1>Política de privacidad</h1>
    <p class="text-slate-500 text-sm">Última actualización: {{ fecha }}</p>

    <h2>1. Información que recopilamos</h2>
    <p>Recopilamos información que nos proporcionas directamente al crear una cuenta, realizar una compra o contactarnos, incluyendo nombre, correo electrónico, dirección de envío y datos de pago.</p>

    <h2>2. Uso de la información</h2>
    <p>Utilizamos tu información para procesar pedidos, enviarte confirmaciones, mejorar nuestros servicios y, con tu consentimiento, enviarte comunicaciones promocionales.</p>

    <h2>3. Compartición de datos</h2>
    <p>No vendemos tu información personal. Podemos compartirla con proveedores de servicios (paquetería, pasarelas de pago) únicamente en la medida necesaria para completar tu pedido.</p>

    <h2>4. Seguridad</h2>
    <p>Implementamos medidas técnicas y organizativas para proteger tu información contra acceso no autorizado, pérdida o alteración.</p>

    <h2>5. Cookies</h2>
    <p>Usamos cookies para mejorar la experiencia de navegación y analizar el tráfico. Puedes desactivarlas en la configuración de tu navegador.</p>

    <h2>6. Tus derechos</h2>
    <p>Tienes derecho a acceder, rectificar o eliminar tus datos personales. Para ejercerlos escríbenos a <a href="mailto:privacidad@mktska.com">privacidad@mktska.com</a>.</p>

    <h2>7. Cambios a esta política</h2>
    <p>Podemos actualizar esta política ocasionalmente. Te notificaremos por correo sobre cambios significativos.</p>
  </div>
</template>

<script setup>
const fecha = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' })
</script>
