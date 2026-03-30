<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 py-12">
    <div class="w-full max-w-md">

      <!-- Card -->
      <div class="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm px-8 py-10">

        <!-- ── PASO 1: Credenciales ────────────────────────────────────── -->
        <template v-if="!requires2fa">
          <!-- Logo / header -->
          <div class="text-center mb-8">
            <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 dark:bg-cyan-500 mb-4">
              <svg class="h-6 w-6 text-white dark:text-slate-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
              </svg>
            </div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Iniciar sesión</h1>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Bienvenido de nuevo</p>
          </div>

          <form @submit.prevent="onSubmit" class="space-y-4" novalidate>

            <!-- Usuario -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Usuario</label>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
                  </svg>
                </span>
                <input
                  v-model="username"
                  type="text"
                  placeholder="Tu usuario"
                  required
                  autocomplete="username"
                  class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <!-- Contraseña -->
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Contraseña</label>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
                  </svg>
                </span>
                <input
                  v-model="password"
                  :type="showPwd ? 'text' : 'password'"
                  placeholder="Tu contraseña"
                  required
                  autocomplete="current-password"
                  class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-10 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
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
            </div>

            <!-- Error -->
            <div v-if="error" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2.5">
              <svg class="h-4 w-4 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
              </svg>
              <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
            </div>

            <!-- Submit -->
            <button type="submit" :disabled="isSubmitting"
              class="relative w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 disabled:opacity-60 transition-colors shadow-sm mt-2">
              <span v-if="!isSubmitting">Entrar</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                Entrando…
              </span>
            </button>
          </form>

          <!-- Divider -->
          <div class="my-6 flex items-center gap-3">
            <div class="flex-1 h-px bg-slate-100 dark:bg-slate-800"></div>
            <span class="text-xs text-slate-400">¿No tienes cuenta?</span>
            <div class="flex-1 h-px bg-slate-100 dark:bg-slate-800"></div>
          </div>

          <!-- Register CTA -->
          <RouterLink to="/registro"
            class="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-slate-200 dark:border-slate-700 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:border-slate-900 dark:hover:border-cyan-500 hover:text-slate-900 dark:hover:text-cyan-400 transition-all">
            Crear cuenta gratis
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
            </svg>
          </RouterLink>
        </template>

        <!-- ── PASO 2: Código 2FA ──────────────────────────────────────── -->
        <template v-else>
          <div class="text-center mb-8">
            <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 dark:bg-cyan-500 mb-4">
              <svg class="h-6 w-6 text-white dark:text-slate-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 1.5H8.25A2.25 2.25 0 006 3.75v16.5a2.25 2.25 0 002.25 2.25h7.5A2.25 2.25 0 0018 20.25V3.75a2.25 2.25 0 00-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 8.25h3m-3 3h3m-3 3h3"/>
              </svg>
            </div>
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Verificación en 2 pasos</h1>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Ingresa el código de tu aplicación autenticadora</p>
          </div>

          <form @submit.prevent="onSubmit2FA" class="space-y-4" novalidate>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Código de 6 dígitos</label>
              <input
                v-model="otpCode"
                ref="otpInput"
                type="text"
                inputmode="numeric"
                pattern="[0-9]*"
                maxlength="6"
                placeholder="000000"
                required
                autocomplete="one-time-code"
                class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-3 px-4 text-center text-2xl tracking-widest font-mono text-slate-900 dark:text-white placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
              />
            </div>

            <!-- Error -->
            <div v-if="error" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2.5">
              <svg class="h-4 w-4 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/>
              </svg>
              <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
            </div>

            <button type="submit" :disabled="isSubmitting || otpCode.length < 6"
              class="relative w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 disabled:opacity-60 transition-colors shadow-sm">
              <span v-if="!isSubmitting">Verificar</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                Verificando…
              </span>
            </button>

            <button type="button" @click="cancelar2FA"
              class="w-full text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors pt-1">
              ← Volver al inicio de sesión
            </button>
          </form>
        </template>

      </div>

      <!-- Benefits hint -->
      <p class="mt-5 text-center text-xs text-slate-400 dark:text-slate-600">
        Al iniciar sesión puedes rastrear pedidos, guardar favoritos y agilizar tus compras.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'

defineOptions({ name: 'LoginView' })

const username = ref('')
const password = ref('')
const showPwd  = ref(false)
const error    = ref('')
const isSubmitting = ref(false)
const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()
const carrito = useCarritoStore()

// Estado 2FA
const requires2fa = ref(false)
const challenge    = ref('')
const otpCode      = ref('')
const otpInput     = ref(null)

let inFlightController = null
let debounceTimer

const redirectTo = () => route.query.redirect ? String(route.query.redirect) : '/productos'

const onSubmit = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    inFlightController?.abort()
    inFlightController = new AbortController()
    isSubmitting.value = true
    error.value = ''
    try {
      const data = await auth.login({ username: username.value, password: password.value }, inFlightController.signal)

      if (data?.requires_2fa) {
        challenge.value = data.challenge
        requires2fa.value = true
        await nextTick()
        otpInput.value?.focus()
        return
      }

      await carrito.cargar()
      router.push(redirectTo())
    } catch (err) {
      if (err.name === 'CanceledError') return
      error.value = err.response?.status === 401 ? 'Usuario o contraseña incorrectos' : 'Error al iniciar sesión'
    } finally {
      isSubmitting.value = false
    }
  }, 300)
}

const onSubmit2FA = async () => {
  isSubmitting.value = true
  error.value = ''
  try {
    await auth.loginWith2FA({ challenge: challenge.value, otp: otpCode.value })
    await carrito.cargar()
    router.push(redirectTo())
  } catch (err) {
    error.value = err.message || 'Código incorrecto'
    otpCode.value = ''
    otpInput.value?.focus()
  } finally {
    isSubmitting.value = false
  }
}

const cancelar2FA = () => {
  requires2fa.value = false
  challenge.value = ''
  otpCode.value = ''
  error.value = ''
}
</script>
