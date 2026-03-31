<template>
  <main class="bg-slate-50 min-h-screen px-4 py-16 flex items-center justify-center">
    <div class="mx-auto max-w-lg w-full space-y-6 text-center">

      <!-- Ícono -->
      <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-red-600 text-3xl mx-auto">
        ✕
      </div>

      <div class="space-y-2">
        <h1 class="text-2xl font-semibold text-slate-900">El pago no se completó</h1>
        <p class="text-slate-600">
          Tu pedido
          <span v-if="externalRef" class="font-semibold text-slate-900">#{{ externalRef }}</span>
          sigue pendiente. No se realizó ningún cargo.
        </p>
        <p class="text-sm text-slate-500">
          Puedes intentarlo de nuevo o elegir otro método de pago.
        </p>
      </div>

      <!-- Razón del fallo si la hay -->
      <div v-if="statusDetail" class="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
        {{ statusDetail }}
      </div>

      <!-- Acciones -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center pt-2">
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-full bg-slate-900 px-6 py-3 text-white font-semibold shadow-sm hover:bg-slate-800 transition-colors"
          @click="reintentar"
        >
          Reintentar pago
        </button>
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-full border border-slate-300 bg-white px-6 py-3 text-slate-700 font-semibold hover:bg-slate-50 transition-colors"
          @click="irAlInicio"
        >
          Ir al inicio
        </button>
      </div>

      <!-- WhatsApp ayuda -->
      <p class="text-sm text-slate-500">
        ¿Necesitas ayuda?
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

useHead({ title: 'Pago no completado — Mktska Digital' })

const route = useRoute()
const router = useRouter()

const externalRef = computed(() => route.query.external_reference || null)

const STATUS_MESSAGES = {
  cc_rejected_insufficient_amount: 'Fondos insuficientes en la tarjeta.',
  cc_rejected_bad_filled_card_number: 'Número de tarjeta incorrecto.',
  cc_rejected_bad_filled_date: 'Fecha de vencimiento incorrecta.',
  cc_rejected_bad_filled_security_code: 'Código de seguridad incorrecto.',
  cc_rejected_call_for_authorize: 'El banco requiere autorización. Comunícate con tu banco.',
  cc_rejected_card_disabled: 'Tarjeta deshabilitada. Comunícate con tu banco.',
  cc_rejected_duplicated_payment: 'Pago duplicado. Ya existe un pago con el mismo importe.',
  cc_rejected_high_risk: 'El pago fue rechazado por medidas de seguridad.',
}

const statusDetail = computed(() => {
  const reason = route.query.collection_status || route.query.status
  return STATUS_MESSAGES[reason] || null
})

const reintentar = () => {
  // Limpiar el estado de pedido pendiente para que el checkout no muestre la advertencia
  try { sessionStorage.removeItem('mp_pending_order') } catch { /* */ }
  if (externalRef.value) {
    router.push({ name: 'checkout', query: { pedido: externalRef.value } })
  } else {
    router.push({ name: 'checkout' })
  }
}

const irAlInicio = () => router.push({ name: 'home' })
</script>
