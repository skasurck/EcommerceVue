<template>
  <div class="max-w-2xl mx-auto px-4 py-6 space-y-8">

    <div>
      <h3 class="text-xl font-semibold text-slate-900 dark:text-slate-100">Métodos de pago</h3>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Configura los datos que verán los clientes al pagar.</p>
    </div>

    <!-- Mercado Pago (informativo) -->
    <div class="rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="px-5 py-4 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-[#009ee3] flex items-center justify-center shrink-0">
          <svg viewBox="0 0 48 48" class="w-5 h-5 fill-white" xmlns="http://www.w3.org/2000/svg">
            <path d="M24 4C12.95 4 4 12.95 4 24s8.95 20 20 20 20-8.95 20-20S35.05 4 24 4zm0 6c7.73 0 14 6.27 14 14 0 2.35-.58 4.56-1.62 6.5L13.5 11.62C15.44 10.58 17.65 10 20 10h4zm0 28c-7.73 0-14-6.27-14-14 0-2.35.58-4.56 1.62-6.5l22.88 22.88A13.94 13.94 0 0 1 28 38h-4z"/>
          </svg>
        </div>
        <div>
          <p class="font-semibold text-sm text-slate-800 dark:text-slate-100">Mercado Pago</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Activo — configurado desde el panel de MP</p>
        </div>
        <span class="ml-auto inline-flex items-center gap-1 text-xs font-medium text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 rounded-full px-2.5 py-0.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>Activo
        </span>
      </div>
      <div class="px-5 py-4 text-sm text-slate-500 dark:text-slate-400">
        Acepta tarjetas, OXXO, transferencias y más. Las credenciales se gestionan en
        <strong class="text-slate-700 dark:text-slate-300">Configuración → Variables de entorno</strong>.
      </div>
    </div>

    <!-- Transferencia bancaria -->
    <div class="rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="px-5 py-4 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z" />
          </svg>
        </div>
        <div>
          <p class="font-semibold text-sm text-slate-800 dark:text-slate-100">Transferencia bancaria</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Los datos se muestran al cliente al seleccionar este método</p>
        </div>
        <!-- Toggle activo/oculto -->
        <label class="ml-auto flex items-center gap-2 cursor-pointer">
          <span class="text-xs text-slate-500 dark:text-slate-400">{{ form.activa ? 'Activo' : 'Oculto' }}</span>
          <button
            type="button"
            @click="form.activa = !form.activa"
            :class="form.activa ? 'bg-cyan-500' : 'bg-slate-300 dark:bg-slate-600'"
            class="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none"
          >
            <span
              :class="form.activa ? 'translate-x-4' : 'translate-x-1'"
              class="inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform shadow"
            />
          </button>
        </label>
      </div>

      <form @submit.prevent="guardar" class="px-5 py-5 space-y-4">

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Banco</label>
            <input v-model="form.banco" placeholder="Ej. BBVA, Banamex, HSBC…" :class="inputClass" />
          </div>
          <div class="space-y-1">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Beneficiario</label>
            <input v-model="form.beneficiario" placeholder="Nombre del titular de la cuenta" :class="inputClass" />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="space-y-1">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">CLABE interbancaria</label>
            <input v-model="form.clabe" placeholder="18 dígitos" maxlength="18" inputmode="numeric" :class="inputClass" />
            <p v-if="form.clabe && form.clabe.length !== 18" class="text-xs text-amber-500">La CLABE debe tener 18 dígitos</p>
          </div>
          <div class="space-y-1">
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Número de cuenta <span class="text-xs text-slate-400">(opcional)</span>
            </label>
            <input v-model="form.numero_cuenta" placeholder="Ej. 1234567890" :class="inputClass" />
          </div>
        </div>

        <div class="space-y-1">
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Instrucciones adicionales <span class="text-xs text-slate-400">(opcional)</span>
          </label>
          <textarea
            v-model="form.instrucciones"
            rows="2"
            placeholder="Ej. Envía tu comprobante al correo ventas@tutienda.com para confirmar tu pedido."
            class="w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 resize-none transition-colors"
          />
        </div>

        <!-- Vista previa -->
        <div v-if="form.banco || form.clabe || form.beneficiario" class="rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 p-4 text-sm space-y-1.5">
          <p class="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wide mb-2">Vista previa en checkout</p>
          <div v-if="form.banco" class="flex justify-between">
            <span class="text-slate-500 dark:text-slate-400">Banco</span>
            <span class="font-medium text-slate-800 dark:text-slate-100">{{ form.banco }}</span>
          </div>
          <div v-if="form.clabe" class="flex justify-between">
            <span class="text-slate-500 dark:text-slate-400">CLABE</span>
            <span class="font-mono font-medium text-slate-800 dark:text-slate-100">{{ form.clabe }}</span>
          </div>
          <div v-if="form.numero_cuenta" class="flex justify-between">
            <span class="text-slate-500 dark:text-slate-400">Núm. cuenta</span>
            <span class="font-mono font-medium text-slate-800 dark:text-slate-100">{{ form.numero_cuenta }}</span>
          </div>
          <div v-if="form.beneficiario" class="flex justify-between">
            <span class="text-slate-500 dark:text-slate-400">Beneficiario</span>
            <span class="font-medium text-slate-800 dark:text-slate-100">{{ form.beneficiario }}</span>
          </div>
          <p v-if="form.instrucciones" class="text-xs text-amber-600 dark:text-amber-400 pt-2 border-t border-slate-200 dark:border-slate-700 mt-1">
            {{ form.instrucciones }}
          </p>
        </div>

        <!-- Acciones -->
        <div class="flex items-center justify-between pt-2">
          <p v-if="guardado" class="text-sm text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            Guardado correctamente
          </p>
          <p v-else-if="errorMsg" class="text-sm text-rose-500">{{ errorMsg }}</p>
          <span v-else />
          <button
            type="submit"
            :disabled="guardando"
            class="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-white font-semibold text-sm shadow-sm transition-colors"
          >
            {{ guardando ? 'Guardando…' : 'Guardar cambios' }}
          </button>
        </div>

      </form>
    </div>

  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import axios from '@/axios'

defineOptions({ name: 'MetodosPago' })

const form = reactive({
  banco: '', clabe: '', numero_cuenta: '', beneficiario: '', instrucciones: '', activa: true,
})
const guardando = ref(false)
const guardado  = ref(false)
const errorMsg  = ref('')

const inputClass = 'w-full rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 transition-colors'

onMounted(async () => {
  try {
    const { data } = await axios.get('/pagos/transferencia/config/')
    Object.assign(form, data)
  } catch { /* sin datos previos */ }
})

const guardar = async () => {
  guardando.value = true
  guardado.value  = false
  errorMsg.value  = ''
  try {
    await axios.put('/pagos/transferencia/config/', { ...form })
    guardado.value = true
    setTimeout(() => { guardado.value = false }, 3000)
  } catch {
    errorMsg.value = 'No se pudieron guardar los cambios.'
  } finally {
    guardando.value = false
  }
}
</script>
