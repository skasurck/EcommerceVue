<template>
  <div class="max-w-3xl mx-auto px-4 py-10 prose prose-slate">
    <h1>Política de devoluciones</h1>
    <p class="text-slate-500 text-sm">Última actualización: {{ fecha }}</p>

    <h2>1. Plazo de devolución</h2>
    <p>Aceptamos devoluciones dentro de los <strong>30 días naturales</strong> posteriores a la fecha de entrega, siempre que el producto esté en su estado original, sin uso y con empaque completo.</p>

    <h2>2. Productos no elegibles</h2>
    <ul>
      <li>Productos con daños causados por el usuario.</li>
      <li>Productos sin empaque original o con sellos de garantía rotos.</li>
      <li>Software, licencias digitales o tarjetas de regalo.</li>
      <li>Productos personalizados o bajo pedido especial.</li>
    </ul>

    <h2>3. Proceso de devolución</h2>
    <ol>
      <li>Contáctanos en <a href="mailto:devoluciones@mktska.com">devoluciones@mktska.com</a> indicando tu número de pedido y motivo.</li>
      <li>Te enviaremos instrucciones y una guía de envío prepagada.</li>
      <li>Una vez recibido e inspeccionado el producto, procesaremos el reembolso en un plazo de 5 a 10 días hábiles.</li>
    </ol>

    <h2>4. Productos defectuosos</h2>
    <p>Si recibes un producto defectuoso o dañado en el envío, contáctanos dentro de las primeras <strong>72 horas</strong> de recibido. Te enviaremos un reemplazo sin costo adicional.</p>

    <h2>5. Reembolsos</h2>
    <p>Los reembolsos se realizarán mediante el mismo método de pago utilizado en la compra. El tiempo de acreditación depende de tu banco o institución financiera.</p>

    <h2>6. Cambios</h2>
    <p>Si deseas cambiar un producto por otro, realiza una devolución y efectúa una nueva compra para garantizar disponibilidad.</p>
  </div>
</template>

<script setup>
const fecha = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' })
</script>
