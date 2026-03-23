<template>
  <div class="max-w-3xl mx-auto px-4 py-10 prose prose-slate">
    <h1>Términos y condiciones</h1>
    <p class="text-slate-500 text-sm">Última actualización: {{ fecha }}</p>

    <h2>1. Aceptación</h2>
    <p>Al acceder y utilizar este sitio web aceptas estos términos y condiciones en su totalidad. Si no estás de acuerdo, te pedimos que no utilices nuestros servicios.</p>

    <h2>2. Productos y precios</h2>
    <p>Nos reservamos el derecho de modificar precios, descripciones y disponibilidad de productos en cualquier momento sin previo aviso. Los precios mostrados incluyen IVA salvo indicación contraria.</p>

    <h2>3. Proceso de compra</h2>
    <p>Al confirmar tu pedido recibirás un correo de confirmación. El contrato de compraventa se perfecciona en el momento en que enviamos dicha confirmación.</p>

    <h2>4. Pagos</h2>
    <p>Aceptamos transferencia bancaria, tarjeta de crédito/débito y Mercado Pago. Todos los pagos son procesados de forma segura.</p>

    <h2>5. Envíos</h2>
    <p>Los tiempos de entrega son estimados y pueden variar. No nos hacemos responsables por retrasos causados por la paquetería o situaciones fuera de nuestro control.</p>

    <h2>6. Propiedad intelectual</h2>
    <p>Todo el contenido de este sitio (imágenes, textos, logos) es propiedad de Mktska Digital y está protegido por derechos de autor.</p>

    <h2>7. Limitación de responsabilidad</h2>
    <p>No seremos responsables por daños indirectos, incidentales o consecuentes derivados del uso de nuestros productos o servicios.</p>

    <h2>8. Ley aplicable</h2>
    <p>Estos términos se rigen por las leyes de los Estados Unidos Mexicanos. Cualquier disputa se someterá a los tribunales competentes de la Ciudad de México.</p>
  </div>
</template>

<script setup>
const fecha = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' })
</script>
