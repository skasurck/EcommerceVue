<template>
  <main class="bg-slate-50 min-h-screen px-4 py-16 flex items-center justify-center">
    <div class="mx-auto max-w-lg w-full space-y-6 text-center">

      <!-- Ícono -->
      <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100 text-yellow-600 text-3xl mx-auto">
        ⏳
      </div>

      <div class="space-y-2">
        <h1 class="text-2xl font-semibold text-slate-900">Pago en proceso</h1>
        <p class="text-slate-600">
          Tu pedido
          <span v-if="externalRef" class="font-semibold text-slate-900">#{{ externalRef }}</span>
          está siendo procesado por Mercado Pago.
        </p>
        <p class="text-sm text-slate-500">
          Te notificaremos cuando el pago sea confirmado. Esto puede tardar unos minutos.
        </p>
      </div>

      <!-- Información -->
      <div class="rounded-lg bg-yellow-50 border border-yellow-200 px-5 py-4 text-sm text-yellow-800 text-left space-y-1">
        <p class="font-semibold">¿Qué pasa ahora?</p>
        <ul class="list-disc list-inside space-y-1 text-yellow-700">
          <li>Mercado Pago está validando tu pago.</li>
          <li>Recibirás un correo cuando sea confirmado.</li>
          <li>Tu pedido será preparado una vez confirmado el pago.</li>
        </ul>
      </div>

      <!-- Acciones -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center pt-2">
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-full bg-slate-900 px-6 py-3 text-white font-semibold shadow-sm hover:bg-slate-800 transition-colors"
          @click="verPedidos"
        >
          Ver mis pedidos
        </button>
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-full border border-slate-300 bg-white px-6 py-3 text-slate-700 font-semibold hover:bg-slate-50 transition-colors"
          @click="irAlInicio"
        >
          Seguir comprando
        </button>
      </div>

      <!-- WhatsApp ayuda -->
      <p class="text-sm text-slate-500">
        ¿Tienes dudas?
        <a
          href="https://wa.me/525571666346"
          target="_blank"
          rel="noopener noreferrer"
          class="text-green-600 font-medium hover:underline"
        >
          Escríbenos por WhatsApp
        </a>
      </p>

    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@vueuse/head'

useHead({ title: 'Pago en proceso — Mktska Digital' })

const route = useRoute()
const router = useRouter()

const externalRef = computed(() => route.query.external_reference || null)

const verPedidos = () => router.push({ name: 'mis-pedidos' })
const irAlInicio = () => router.push({ name: 'home' })
</script>
