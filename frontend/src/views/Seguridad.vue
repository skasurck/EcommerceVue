<template>
  <main class="min-h-screen bg-slate-50 dark:bg-slate-900 px-4 py-8">
    <div class="mx-auto max-w-lg space-y-5">

      <div class="flex items-center gap-3">
        <RouterLink to="/mi-cuenta" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </RouterLink>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-slate-100">Seguridad</h1>
      </div>

      <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
        <div class="flex items-center gap-3 mb-6">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-700">
            <svg class="h-5 w-5 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <div>
            <h2 class="text-base font-semibold text-slate-900 dark:text-slate-100">Cambiar contraseña</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400">Elige una contraseña segura de al menos 8 caracteres</p>
          </div>
        </div>

        <!-- Alerta error -->
        <div v-if="errorMsg" class="mb-4 rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/30 px-4 py-3 text-sm text-red-700 dark:text-red-400">
          {{ errorMsg }}
        </div>

        <!-- Alerta éxito -->
        <div v-if="okMsg" class="mb-4 rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/30 px-4 py-3 text-sm text-emerald-700 dark:text-emerald-400 flex items-center gap-2">
          <svg class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          {{ okMsg }}
        </div>

        <form @submit.prevent="enviar" class="space-y-4">
          <!-- Contraseña actual -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">
              Contraseña actual
            </label>
            <div class="relative">
              <input
                v-model="form.old_password"
                :type="showOld ? 'text' : 'password'"
                placeholder="Tu contraseña actual"
                autocomplete="current-password"
                :class="[inputClass, fieldError.old_password ? 'border-red-400 focus:ring-red-400' : '']"
              />
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" @click="showOld = !showOld">
                <svg v-if="showOld" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                </svg>
                <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
            <p v-if="fieldError.old_password" class="mt-1 text-xs text-red-500">{{ fieldError.old_password }}</p>
          </div>

          <!-- Nueva contraseña -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">
              Nueva contraseña
            </label>
            <div class="relative">
              <input
                v-model="form.new_password"
                :type="showNew ? 'text' : 'password'"
                placeholder="Mínimo 8 caracteres"
                autocomplete="new-password"
                :class="[inputClass, fieldError.new_password ? 'border-red-400 focus:ring-red-400' : '']"
              />
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" @click="showNew = !showNew">
                <svg v-if="showNew" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                </svg>
                <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
            <!-- Barra de fortaleza -->
            <div v-if="form.new_password" class="mt-2 flex gap-1">
              <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-colors" :class="strengthBar(i)" />
            </div>
            <p v-if="form.new_password" class="mt-1 text-xs" :class="strengthTextClass">{{ strengthText }}</p>
            <p v-if="fieldError.new_password" class="mt-1 text-xs text-red-500">{{ fieldError.new_password }}</p>
          </div>

          <!-- Confirmar contraseña -->
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-1.5">
              Confirmar nueva contraseña
            </label>
            <div class="relative">
              <input
                v-model="form.confirmar"
                :type="showConfirm ? 'text' : 'password'"
                placeholder="Repite la nueva contraseña"
                autocomplete="new-password"
                :class="[inputClass, fieldError.confirmar ? 'border-red-400 focus:ring-red-400' : '']"
              />
              <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" @click="showConfirm = !showConfirm">
                <svg v-if="showConfirm" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18" />
                </svg>
                <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
            <p v-if="fieldError.confirmar" class="mt-1 text-xs text-red-500">{{ fieldError.confirmar }}</p>
          </div>

          <button
            type="submit"
            :disabled="enviando"
            class="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-60 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            <svg v-if="enviando" class="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            {{ enviando ? 'Guardando…' : 'Actualizar contraseña' }}
          </button>
        </form>
      </section>

    </div>
  </main>
</template>

<script setup>
defineOptions({ name: 'SeguridadView' })
import { ref, computed } from 'vue'
import { cambiarPassword } from '@/services/account'

const form = ref({ old_password: '', new_password: '', confirmar: '' })
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)
const enviando = ref(false)
const errorMsg = ref('')
const okMsg = ref('')
const fieldError = ref({})

const inputClass = 'w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2.5 pr-10 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition'

// Fortaleza de contraseña
const strengthScore = computed(() => {
  const p = form.value.new_password
  if (!p) return 0
  let score = 0
  if (p.length >= 8) score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p) && /[a-z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return Math.min(score, 4)
})

const strengthBar = (i) => {
  if (strengthScore.value < i) return 'bg-slate-200 dark:bg-slate-600'
  if (strengthScore.value === 1) return 'bg-red-400'
  if (strengthScore.value === 2) return 'bg-orange-400'
  if (strengthScore.value === 3) return 'bg-yellow-400'
  return 'bg-emerald-500'
}

const strengthText = computed(() => ['', 'Muy débil', 'Débil', 'Moderada', 'Fuerte'][strengthScore.value] ?? '')
const strengthTextClass = computed(() => ({
  1: 'text-red-500', 2: 'text-orange-500', 3: 'text-yellow-600', 4: 'text-emerald-600 dark:text-emerald-400',
}[strengthScore.value] ?? 'text-slate-500'))

const validar = () => {
  const errs = {}
  if (!form.value.old_password) errs.old_password = 'Ingresa tu contraseña actual'
  if (!form.value.new_password) errs.new_password = 'Ingresa una nueva contraseña'
  else if (form.value.new_password.length < 8) errs.new_password = 'Mínimo 8 caracteres'
  if (!form.value.confirmar) errs.confirmar = 'Confirma la nueva contraseña'
  else if (form.value.confirmar !== form.value.new_password) errs.confirmar = 'Las contraseñas no coinciden'
  fieldError.value = errs
  return Object.keys(errs).length === 0
}

const enviar = async () => {
  errorMsg.value = ''
  okMsg.value = ''
  if (!validar()) return
  enviando.value = true
  try {
    await cambiarPassword({ old_password: form.value.old_password, new_password: form.value.new_password })
    form.value = { old_password: '', new_password: '', confirmar: '' }
    fieldError.value = {}
    okMsg.value = 'Contraseña actualizada correctamente.'
    setTimeout(() => { okMsg.value = '' }, 5000)
  } catch (e) {
    const detail = e?.response?.data
    if (typeof detail === 'object') {
      const msg = Object.values(detail).flat().join(' ')
      errorMsg.value = msg || 'Error al cambiar la contraseña.'
    } else {
      errorMsg.value = 'Error al cambiar la contraseña.'
    }
  } finally {
    enviando.value = false
  }
}
</script>
