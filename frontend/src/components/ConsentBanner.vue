<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:max-w-md
             bg-slate-900 text-white p-4 rounded-xl shadow-2xl z-50
             border border-slate-700"
      role="dialog"
      aria-live="polite"
      aria-label="Aviso de cookies y tracking"
    >
      <p class="text-sm leading-relaxed mb-3">
        Usamos cookies y datos de navegación para recordar tu carrito y mostrarte
        productos relevantes.
        <router-link to="/privacidad" class="underline text-cyan-300 hover:text-cyan-200">
          Aviso de privacidad
        </router-link>.
      </p>
      <div class="flex gap-2">
        <button
          type="button"
          class="bg-cyan-500 hover:bg-cyan-400 text-slate-900 font-medium
                 px-3 py-1.5 rounded text-sm transition-colors"
          @click="aceptar"
        >
          Aceptar
        </button>
        <button
          type="button"
          class="px-3 py-1.5 text-sm underline text-slate-300 hover:text-white"
          @click="rechazar"
        >
          Solo lo esencial
        </button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getConsent, setConsent } from '@/composables/useTracking'

const visible = ref(false)

onMounted(() => {
  if (!getConsent()) visible.value = true
})

function aceptar() {
  setConsent({ analytics: true, personalizacion: true })
  visible.value = false
}

function rechazar() {
  setConsent({ analytics: false, personalizacion: false })
  visible.value = false
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
