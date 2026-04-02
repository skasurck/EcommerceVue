<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4">
    <div class="w-full max-w-sm rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-6 shadow-md">

      <!-- Éxito -->
      <div v-if="success" class="flex flex-col items-center text-center gap-4">
        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 dark:bg-emerald-500/10">
          <svg class="h-7 w-7 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
          </svg>
        </div>
        <div>
          <p class="font-semibold text-slate-900 dark:text-white">¡Contraseña actualizada!</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Ya puedes iniciar sesión con tu nueva contraseña.</p>
        </div>
        <RouterLink
          to="/login"
          class="w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 text-center hover:bg-slate-800 dark:hover:bg-cyan-400 transition-colors"
        >
          Ir al inicio de sesión
        </RouterLink>
      </div>

      <!-- Token inválido / expirado -->
      <div v-else-if="tokenInvalid" class="flex flex-col items-center text-center gap-4">
        <div class="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 dark:bg-red-500/10">
          <svg class="h-7 w-7 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
          </svg>
        </div>
        <div>
          <p class="font-semibold text-slate-900 dark:text-white">Enlace inválido o expirado</p>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ tokenError }}</p>
        </div>
        <RouterLink
          to="/checkout"
          class="text-sm text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          Solicitar nuevo enlace
        </RouterLink>
      </div>

      <!-- Formulario nueva contraseña -->
      <template v-else>
        <div class="mb-5">
          <div class="mb-3 inline-flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800">
            <svg class="h-5 w-5 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
            </svg>
          </div>
          <h1 class="text-xl font-bold text-slate-900 dark:text-white">Nueva contraseña</h1>
          <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">Elige una contraseña segura para tu cuenta.</p>
        </div>

        <form class="flex flex-col gap-3" @submit.prevent="onSubmit" novalidate>
          <!-- Nueva contraseña -->
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
              </svg>
            </span>
            <input
              v-model="newPassword"
              :type="showPwd ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Nueva contraseña (mín. 8 caracteres)"
              class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-10 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
            />
            <button type="button" tabindex="-1" @click="showPwd = !showPwd"
              class="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
              <svg v-if="!showPwd" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/></svg>
            </button>
          </div>

          <!-- Barra de fuerza -->
          <div v-if="newPassword" class="flex gap-1">
            <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-colors duration-300"
                 :class="i <= pwdStrength ? pwdStrengthColor : 'bg-slate-200 dark:bg-slate-700'"></div>
          </div>

          <!-- Confirmar contraseña -->
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
              </svg>
            </span>
            <input
              v-model="confirmPassword"
              :type="showPwd ? 'text' : 'password'"
              required
              autocomplete="new-password"
              placeholder="Confirmar contraseña"
              class="w-full rounded-xl border py-2.5 pl-10 pr-10 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
              :class="confirmPassword && newPassword === confirmPassword
                ? 'border-emerald-300 dark:border-emerald-500/50 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-emerald-400'
                : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-cyan-500'"
            />
            <span v-if="confirmPassword && newPassword === confirmPassword"
              class="absolute inset-y-0 right-3 flex items-center text-emerald-500">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
            </span>
          </div>

          <!-- Error -->
          <div v-if="formError" class="flex items-start gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2">
            <svg class="h-3.5 w-3.5 shrink-0 mt-0.5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/></svg>
            <p class="text-xs text-red-600 dark:text-red-400">{{ formError }}</p>
          </div>

          <button
            type="submit"
            :disabled="loading || newPassword !== confirmPassword || newPassword.length < 8"
            class="w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 disabled:opacity-60 transition-colors shadow-sm"
          >
            <span v-if="!loading">Guardar nueva contraseña</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
              Guardando…
            </span>
          </button>
        </form>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import api from '@/axios'

const route = useRoute()

const token           = ref('')
const newPassword     = ref('')
const confirmPassword = ref('')
const showPwd         = ref(false)
const loading         = ref(false)
const formError       = ref('')
const success         = ref(false)
const tokenInvalid    = ref(false)
const tokenError      = ref('')

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    tokenInvalid.value = true
    tokenError.value = 'No se encontró el token en el enlace.'
  }
})

const pwdStrength = computed(() => {
  const p = newPassword.value
  if (!p) return 0
  let s = 0
  if (p.length >= 8) s++
  if (/[A-Z]/.test(p)) s++
  if (/[0-9]/.test(p)) s++
  if (/[^A-Za-z0-9]/.test(p)) s++
  return Math.max(1, s)
})
const pwdStrengthColor = computed(() => {
  return ['', 'bg-red-400', 'bg-amber-400', 'bg-yellow-400', 'bg-emerald-500'][pwdStrength.value] || 'bg-slate-200'
})

const onSubmit = async () => {
  formError.value = ''
  if (newPassword.value !== confirmPassword.value) {
    formError.value = 'Las contraseñas no coinciden.'
    return
  }
  if (newPassword.value.length < 8) {
    formError.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }
  loading.value = true
  try {
    await api.post('auth/password-reset/confirm/', {
      token: token.value,
      new_password: newPassword.value,
    })
    success.value = true
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      formError.value = detail.join(' ')
    } else if (typeof detail === 'string') {
      if (detail.includes('expiró') || detail.includes('inválido')) {
        tokenInvalid.value = true
        tokenError.value = detail
      } else {
        formError.value = detail
      }
    } else {
      formError.value = 'No se pudo actualizar la contraseña.'
    }
  } finally {
    loading.value = false
  }
}
</script>
