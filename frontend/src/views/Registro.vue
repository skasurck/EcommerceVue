<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 py-12">
    <div class="w-full max-w-md">

      <!-- Card -->
      <div class="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm px-8 py-10">

        <!-- Header -->
        <div class="text-center mb-8">
          <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 mb-4">
            <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z"/>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Crear cuenta</h1>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Es gratis y solo toma un momento</p>
        </div>

        <!-- Success state -->
        <div v-if="exito" class="text-center py-4">
          <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50 dark:bg-emerald-500/10 mb-4">
            <svg class="h-8 w-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
            </svg>
          </div>
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">¡Cuenta creada!</h2>
          <p class="mt-2 text-sm text-slate-500 dark:text-slate-400">{{ mensaje }}</p>
          <RouterLink
            to="/login"
            class="mt-5 inline-flex items-center gap-2 rounded-xl bg-slate-900 dark:bg-cyan-500 px-6 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 transition-colors"
          >
            Iniciar sesión
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
            </svg>
          </RouterLink>
        </div>

        <!-- Form -->
        <form v-else @submit.prevent="registrar" class="space-y-4" novalidate>

          <!-- Usuario -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Usuario <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
                </svg>
              </span>
              <input
                v-model="username"
                type="text"
                placeholder="Elige un nombre de usuario"
                required
                autocomplete="username"
                class="w-full rounded-xl border py-2.5 pl-10 pr-4 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                :class="errores.username
                  ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400'
                  : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-slate-900 dark:focus:ring-cyan-500'"
              />
            </div>
            <p v-if="errores.username" class="mt-1 text-xs text-red-500">{{ errores.username }}</p>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Correo electrónico <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/>
                </svg>
              </span>
              <input
                v-model="email"
                type="email"
                placeholder="tu@correo.com"
                required
                autocomplete="email"
                class="w-full rounded-xl border py-2.5 pl-10 pr-4 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                :class="errores.email
                  ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400'
                  : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-slate-900 dark:focus:ring-cyan-500'"
              />
            </div>
            <p v-if="errores.email" class="mt-1 text-xs text-red-500">{{ errores.email }}</p>
            <p v-else class="mt-1 text-xs text-slate-400 dark:text-slate-500">Para recuperar tu cuenta y recibir notificaciones de pedidos.</p>
          </div>

          <!-- Contraseña -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Contraseña <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
                </svg>
              </span>
              <input
                v-model="password"
                :type="showPwd ? 'text' : 'password'"
                placeholder="Mínimo 8 caracteres"
                required
                autocomplete="new-password"
                class="w-full rounded-xl border py-2.5 pl-10 pr-10 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                :class="errores.password
                  ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400'
                  : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-slate-900 dark:focus:ring-cyan-500'"
              />
              <button type="button" tabindex="-1" @click="showPwd = !showPwd"
                class="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                <svg v-if="!showPwd" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/>
                </svg>
              </button>
            </div>
            <!-- Strength bar -->
            <div v-if="password" class="mt-2 flex gap-1">
              <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-colors duration-300"
                   :class="i <= pwdStrength ? pwdStrengthColor : 'bg-slate-200 dark:bg-slate-700'"></div>
            </div>
            <p v-if="errores.password" class="mt-1 text-xs text-red-500">{{ errores.password }}</p>
          </div>

          <!-- Confirmar contraseña -->
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Confirmar contraseña <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>
                </svg>
              </span>
              <input
                v-model="passwordConfirm"
                :type="showPwd ? 'text' : 'password'"
                placeholder="Repite la contraseña"
                required
                autocomplete="new-password"
                class="w-full rounded-xl border py-2.5 pl-10 pr-10 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                :class="errores.passwordConfirm
                  ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400'
                  : passwordConfirm && !errores.passwordConfirm
                    ? 'border-emerald-300 dark:border-emerald-500/50 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-emerald-400'
                    : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-slate-900 dark:focus:ring-cyan-500'"
              />
              <!-- Match check -->
              <span v-if="passwordConfirm && password === passwordConfirm"
                class="absolute inset-y-0 right-3 flex items-center text-emerald-500">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
                </svg>
              </span>
            </div>
            <p v-if="errores.passwordConfirm" class="mt-1 text-xs text-red-500">{{ errores.passwordConfirm }}</p>
          </div>

          <!-- Error API -->
          <div v-if="error" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2.5">
            <svg class="h-4 w-4 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
            </svg>
            <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="isSubmitting"
            class="relative w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-2.5 text-sm font-semibold text-white hover:from-cyan-400 hover:to-blue-500 disabled:opacity-60 transition-all shadow-sm shadow-cyan-500/20 mt-2"
          >
            <span v-if="!isSubmitting">Crear mi cuenta</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
              Creando cuenta…
            </span>
          </button>

          <!-- Benefits -->
          <div class="rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 p-3 space-y-1.5">
            <p class="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-2">¿Por qué crear una cuenta?</p>
            <div v-for="b in benefits" :key="b" class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <svg class="h-3.5 w-3.5 shrink-0 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/>
              </svg>
              {{ b }}
            </div>
          </div>
        </form>
      </div>

      <!-- Login CTA -->
      <p v-if="!exito" class="mt-5 text-center text-sm text-slate-500 dark:text-slate-400">
        ¿Ya tienes cuenta?
        <RouterLink to="/login" class="font-semibold text-slate-900 dark:text-cyan-400 hover:underline">
          Inicia sesión
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/axios'

defineOptions({ name: 'RegisterView' })

const username        = ref('')
const email           = ref('')
const password        = ref('')
const passwordConfirm = ref('')
const showPwd         = ref(false)
const mensaje         = ref('')
const error           = ref('')
const exito           = ref(false)
const isSubmitting    = ref(false)
const errores         = ref({})

const benefits = [
  'Rastrea el estado de tus pedidos en tiempo real',
  'Guarda tus productos favoritos',
  'Agiliza el proceso de compra',
  'Recibe notificaciones de ofertas exclusivas',
]

// Password strength 1-4
const pwdStrength = computed(() => {
  const p = password.value
  if (!p) return 0
  let s = 0
  if (p.length >= 8) s++
  if (/[A-Z]/.test(p)) s++
  if (/[0-9]/.test(p)) s++
  if (/[^A-Za-z0-9]/.test(p)) s++
  return Math.max(1, s)
})
const pwdStrengthColor = computed(() => {
  const colors = ['', 'bg-red-400', 'bg-amber-400', 'bg-yellow-400', 'bg-emerald-500']
  return colors[pwdStrength.value] || 'bg-slate-200'
})

const validar = () => {
  const e = {}
  if (!username.value.trim()) e.username = 'El usuario es obligatorio'
  else if (username.value.trim().length < 3) e.username = 'Mínimo 3 caracteres'

  if (!email.value.trim()) e.email = 'El correo es obligatorio'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) e.email = 'Correo no válido'

  if (!password.value) e.password = 'La contraseña es obligatoria'
  else if (password.value.length < 8) e.password = 'Mínimo 8 caracteres'

  if (!passwordConfirm.value) e.passwordConfirm = 'Confirma tu contraseña'
  else if (password.value !== passwordConfirm.value) e.passwordConfirm = 'Las contraseñas no coinciden'

  errores.value = e
  return Object.keys(e).length === 0
}

const registrar = async () => {
  error.value = ''
  if (!validar()) return

  isSubmitting.value = true
  try {
    const res = await api.post('register/', {
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    mensaje.value = res.data.mensaje || '¡Tu cuenta ha sido creada exitosamente!'
    exito.value = true
  } catch (err) {
    const data = err.response?.data
    if (data?.username) error.value = Array.isArray(data.username) ? data.username[0] : data.username
    else if (data?.email) error.value = Array.isArray(data.email) ? data.email[0] : data.email
    else if (data?.password) error.value = Array.isArray(data.password) ? data.password[0] : data.password
    else error.value = 'Error al crear la cuenta. Intenta de nuevo.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
