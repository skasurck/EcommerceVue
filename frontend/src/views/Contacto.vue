<template>
  <div class="max-w-2xl mx-auto px-4 py-10">
    <h1 class="text-3xl font-bold text-slate-900 mb-2">Contacto</h1>
    <p class="text-slate-500 mb-8">Estamos para ayudarte. Escríbenos y te respondemos a la brevedad.</p>

    <div class="grid sm:grid-cols-2 gap-6 mb-10">
      <div class="bg-white border rounded-lg p-5 space-y-1">
        <p class="text-xs uppercase tracking-wider text-slate-400">Correo electrónico</p>
        <a href="mailto:contacto@mktska.com" class="text-slate-800 font-medium hover:underline">contacto@mktska.com</a>
      </div>
      <div class="bg-white border rounded-lg p-5 space-y-1">
        <p class="text-xs uppercase tracking-wider text-slate-400">WhatsApp</p>
        <a href="https://wa.me/521234567890" target="_blank" rel="noopener" class="text-slate-800 font-medium hover:underline">+52 123 456 7890</a>
      </div>
    </div>

    <form @submit.prevent="enviar" class="bg-white border rounded-lg p-6 space-y-4">
      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Nombre</label>
          <input v-model="form.nombre" required placeholder="Tu nombre" class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Correo</label>
          <input v-model="form.email" type="email" required placeholder="tu@correo.com" class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400" />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Asunto</label>
        <input v-model="form.asunto" required placeholder="¿En qué podemos ayudarte?" class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400" />
      </div>
      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Mensaje</label>
        <textarea v-model="form.mensaje" required rows="5" placeholder="Escribe tu mensaje aquí…" class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400 resize-none" />
      </div>
      <p v-if="enviado" class="text-emerald-600 text-sm">¡Mensaje enviado! Te contactaremos pronto.</p>
      <button type="submit" class="rounded-full bg-slate-900 px-6 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 transition-colors">
        Enviar mensaje
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const form   = ref({ nombre: '', email: '', asunto: '', mensaje: '' })
const enviado = ref(false)

const enviar = () => {
  // TODO: conectar con backend o servicio de email
  enviado.value = true
  form.value = { nombre: '', email: '', asunto: '', mensaje: '' }
}
</script>
