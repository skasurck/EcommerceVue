<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="text-center space-y-1">
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">¿Cómo deseas continuar?</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400">Elige una opción para finalizar tu compra.</p>
    </div>

    <!-- Grid: 1 col mobile · 2 cols tablet · 3 cols desktop -->
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">

      <!-- ── LOGIN ─────────────────────────────────────────────── -->
      <section class="rounded-2xl border-2 border-slate-900 dark:border-cyan-500 bg-white dark:bg-slate-900 p-5 shadow-md flex flex-col gap-4 relative overflow-hidden">
        <!-- Badge "Recomendado" -->
        <span class="absolute top-3 right-3 rounded-full bg-slate-900 dark:bg-cyan-500 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white dark:text-slate-900">
          Recomendado
        </span>
        <div>
          <div class="mb-2 inline-flex h-9 w-9 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800">
            <svg class="h-5 w-5 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
            </svg>
          </div>
          <h2 class="text-base font-semibold text-slate-900 dark:text-white">Iniciar sesión</h2>
          <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">Recupera tu carrito y direcciones guardadas.</p>
        </div>

        <!-- Paso 1: Credenciales -->
        <form v-if="!needs2FA && !showForgotPassword" class="flex flex-col gap-3" @submit.prevent="onLogin" novalidate>
          <!-- Usuario -->
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/>
              </svg>
            </span>
            <input
              v-model="loginUsername"
              type="text"
              autocomplete="username"
              required
              placeholder="Usuario"
              class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
            />
          </div>

          <!-- Contraseña -->
          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/>
              </svg>
            </span>
            <input
              v-model="loginPassword"
              :type="showLoginPwd ? 'text' : 'password'"
              autocomplete="current-password"
              required
              placeholder="Contraseña"
              class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-10 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
            />
            <button type="button" tabindex="-1" @click="showLoginPwd = !showLoginPwd"
              class="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
              <svg v-if="!showLoginPwd" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/></svg>
            </button>
          </div>

          <!-- Error login -->
          <div v-if="loginError" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2">
            <svg class="h-3.5 w-3.5 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/></svg>
            <p class="text-xs text-red-600 dark:text-red-400">{{ loginError }}</p>
          </div>

          <button
            type="submit"
            :disabled="loginLoading"
            class="w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 disabled:opacity-60 transition-colors shadow-sm"
          >
            <span v-if="!loginLoading">Entrar</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
              Accediendo…
            </span>
          </button>

          <!-- Link olvidé contraseña -->
          <button type="button" @click="showForgotPassword = true"
            class="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors text-center">
            ¿Olvidaste tu contraseña?
          </button>
        </form>

        <!-- Paso 2: Verificación 2FA -->
        <form v-else-if="needs2FA" class="flex flex-col gap-3" @submit.prevent="onVerify2FA" novalidate>
          <div class="flex items-center gap-2 rounded-xl bg-amber-50 dark:bg-amber-500/10 border border-amber-100 dark:border-amber-500/20 px-3 py-2.5">
            <svg class="h-4 w-4 shrink-0 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/></svg>
            <p class="text-xs text-amber-700 dark:text-amber-400">Ingresa el código de tu app autenticadora.</p>
          </div>

          <div class="relative">
            <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M7.864 4.243A7.5 7.5 0 0119.5 10.5c0 2.92-.556 5.709-1.568 8.268M5.742 6.364A7.465 7.465 0 004.5 10.5a7.464 7.464 0 01-1.15 3.993m1.989 3.559A11.209 11.209 0 008.25 10.5a3.75 3.75 0 117.5 0c0 .527-.021 1.049-.064 1.565M12 10.5a14.94 14.94 0 01-3.6 9.75m6.633-4.596a18.666 18.666 0 01-2.485 5.33"/></svg>
            </span>
            <input
              v-model="otpCode"
              type="text"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              placeholder="Código 6 dígitos"
              class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition tracking-widest"
            />
          </div>

          <div v-if="loginError" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2">
            <svg class="h-3.5 w-3.5 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/></svg>
            <p class="text-xs text-red-600 dark:text-red-400">{{ loginError }}</p>
          </div>

          <button
            type="submit"
            :disabled="loginLoading || otpCode.length !== 6"
            class="w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 disabled:opacity-60 transition-colors shadow-sm"
          >
            <span v-if="!loginLoading">Verificar</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
              Verificando…
            </span>
          </button>
          <button type="button" @click="cancelar2FA"
            class="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors text-center">
            Volver al inicio de sesión
          </button>
        </form>

        <!-- Paso: Recuperar contraseña -->
        <div v-else-if="showForgotPassword" class="flex flex-col gap-3">
          <div v-if="!forgotSent">
            <p class="text-xs text-slate-500 dark:text-slate-400 mb-3">
              Ingresa tu usuario o correo y te enviaremos instrucciones para restablecer tu contraseña.
            </p>
            <form class="flex flex-col gap-3" @submit.prevent="onForgotPassword" novalidate>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/></svg>
                </span>
                <input
                  v-model="forgotIdentifier"
                  type="text"
                  required
                  placeholder="Usuario o correo electrónico"
                  class="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 dark:focus:ring-cyan-500 focus:border-transparent transition"
                />
              </div>

              <div v-if="forgotError" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2">
                <svg class="h-3.5 w-3.5 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/></svg>
                <p class="text-xs text-red-600 dark:text-red-400">{{ forgotError }}</p>
              </div>

              <button
                type="submit"
                :disabled="forgotLoading"
                class="w-full rounded-xl bg-slate-900 dark:bg-cyan-500 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-800 dark:hover:bg-cyan-400 disabled:opacity-60 transition-colors shadow-sm"
              >
                <span v-if="!forgotLoading">Enviar instrucciones</span>
                <span v-else class="flex items-center justify-center gap-2">
                  <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                  Enviando…
                </span>
              </button>
              <button type="button" @click="showForgotPassword = false"
                class="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors text-center">
                Volver al inicio de sesión
              </button>
            </form>
          </div>

          <!-- Éxito: correo enviado -->
          <div v-else class="flex flex-col items-center text-center gap-3 py-2">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 dark:bg-emerald-500/10">
              <svg class="h-6 w-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/></svg>
            </div>
            <div>
              <p class="font-semibold text-slate-900 dark:text-white text-sm">Revisa tu correo</p>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Si el usuario existe, recibirás instrucciones para restablecer tu contraseña.</p>
            </div>
            <button type="button" @click="showForgotPassword = false; forgotSent = false"
              class="text-xs text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
              Volver al inicio de sesión
            </button>
          </div>
        </div>
      </section>

      <!-- ── REGISTER ───────────────────────────────────────────── -->
      <section class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5 shadow-sm flex flex-col gap-4 relative overflow-hidden">

        <!-- Success state -->
        <div v-if="registerSuccess" class="flex flex-1 flex-col items-center justify-center text-center py-4 gap-3">
          <div class="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 dark:bg-emerald-500/10">
            <svg class="h-7 w-7 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
          </div>
          <div>
            <p class="font-semibold text-slate-900 dark:text-white text-sm">¡Cuenta creada!</p>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ registerMessage }}</p>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400">Ahora inicia sesión para continuar.</p>
        </div>

        <template v-else>
          <div>
            <div class="mb-2 inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-100 to-blue-100 dark:from-cyan-500/20 dark:to-blue-600/20">
              <svg class="h-5 w-5 text-cyan-600 dark:text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z"/>
              </svg>
            </div>
            <h2 class="text-base font-semibold text-slate-900 dark:text-white">Registrarme</h2>
            <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">Guarda tu historial y agiliza futuras compras.</p>
          </div>

          <form class="flex flex-col gap-3" @submit.prevent="onRegister" novalidate>
            <!-- Usuario -->
            <div>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"/></svg>
                </span>
                <input
                  v-model="registerUsername"
                  type="text"
                  required
                  placeholder="Usuario"
                  autocomplete="username"
                  class="w-full rounded-xl border py-2.5 pl-10 pr-4 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                  :class="regErr.username ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400' : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-cyan-500'"
                />
              </div>
              <p v-if="regErr.username" class="mt-1 text-xs text-red-500">{{ regErr.username }}</p>
            </div>

            <!-- Email -->
            <div>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"/></svg>
                </span>
                <input
                  v-model="registerEmail"
                  type="email"
                  required
                  placeholder="Correo electrónico"
                  autocomplete="email"
                  class="w-full rounded-xl border py-2.5 pl-10 pr-4 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                  :class="regErr.email ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400' : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-cyan-500'"
                />
              </div>
              <p v-if="regErr.email" class="mt-1 text-xs text-red-500">{{ regErr.email }}</p>
            </div>

            <!-- Contraseña -->
            <div>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"/></svg>
                </span>
                <input
                  v-model="registerPassword"
                  :type="showRegPwd ? 'text' : 'password'"
                  required
                  placeholder="Contraseña (mín. 8 caracteres)"
                  autocomplete="new-password"
                  class="w-full rounded-xl border py-2.5 pl-10 pr-10 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                  :class="regErr.password ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400' : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-cyan-500'"
                />
                <button type="button" tabindex="-1" @click="showRegPwd = !showRegPwd"
                  class="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                  <svg v-if="!showRegPwd" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                  <svg v-else class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88"/></svg>
                </button>
              </div>
              <!-- Strength bar -->
              <div v-if="registerPassword" class="mt-1.5 flex gap-1">
                <div v-for="i in 4" :key="i" class="h-1 flex-1 rounded-full transition-colors duration-300"
                     :class="i <= pwdStrength ? pwdStrengthColor : 'bg-slate-200 dark:bg-slate-700'"></div>
              </div>
              <p v-if="regErr.password" class="mt-1 text-xs text-red-500">{{ regErr.password }}</p>
            </div>

            <!-- Confirmar contraseña -->
            <div>
              <div class="relative">
                <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/></svg>
                </span>
                <input
                  v-model="registerPasswordConfirm"
                  :type="showRegPwd ? 'text' : 'password'"
                  required
                  placeholder="Confirmar contraseña"
                  autocomplete="new-password"
                  class="w-full rounded-xl border py-2.5 pl-10 pr-10 text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition"
                  :class="regErr.passwordConfirm
                    ? 'border-red-300 dark:border-red-500/50 bg-red-50 dark:bg-red-500/5 text-slate-900 dark:text-white focus:ring-red-400'
                    : registerPasswordConfirm && registerPassword === registerPasswordConfirm
                      ? 'border-emerald-300 dark:border-emerald-500/50 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-emerald-400'
                      : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-cyan-500'"
                />
                <span v-if="registerPasswordConfirm && registerPassword === registerPasswordConfirm"
                  class="absolute inset-y-0 right-3 flex items-center text-emerald-500">
                  <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
                </span>
              </div>
              <p v-if="regErr.passwordConfirm" class="mt-1 text-xs text-red-500">{{ regErr.passwordConfirm }}</p>
            </div>

            <!-- Error API -->
            <div v-if="registerError" class="flex items-center gap-2 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-100 dark:border-red-500/20 px-3 py-2">
              <svg class="h-3.5 w-3.5 shrink-0 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"/></svg>
              <p class="text-xs text-red-600 dark:text-red-400">{{ registerError }}</p>
            </div>

            <button
              type="submit"
              :disabled="registerLoading"
              class="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 py-2.5 text-sm font-semibold text-white hover:from-cyan-400 hover:to-blue-500 disabled:opacity-60 transition-all shadow-sm shadow-cyan-500/20"
            >
              <span v-if="!registerLoading">Crear cuenta</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>
                Creando cuenta…
              </span>
            </button>
          </form>
        </template>
      </section>

      <!-- ── GUEST ──────────────────────────────────────────────── -->
      <!-- sm: franja horizontal full-width (col-span-2) · lg: card normal (col-span-1) -->
      <section class="sm:col-span-2 lg:col-span-1 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50 p-5 flex flex-col sm:flex-row lg:flex-col items-start sm:items-center lg:items-start gap-4">

        <!-- Info -->
        <div class="flex items-start sm:items-center lg:items-start gap-3 flex-1 min-w-0">
          <div class="shrink-0 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-slate-200 dark:bg-slate-800">
            <svg class="h-5 w-5 text-slate-500 dark:text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z"/>
            </svg>
          </div>
          <div class="min-w-0">
            <h2 class="text-base font-semibold text-slate-900 dark:text-white">Continuar como invitado</h2>
            <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
              Sin cuenta. Rápido y sin registros. Puedes crear tu cuenta después.
            </p>
          </div>
        </div>

        <!-- Button -->
        <button
          type="button"
          class="shrink-0 w-full sm:w-auto lg:w-full rounded-xl border-2 border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-5 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:border-slate-500 dark:hover:border-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"
          @click="emit('guest')"
        >
          Seguir como invitado
        </button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/axios'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'

const emit = defineEmits(['guest', 'logged-in'])

const auth    = useAuthStore()
const carrito = useCarritoStore()

// ── Login ────────────────────────────────────────────────────────────────────
const loginUsername = ref('')
const loginPassword = ref('')
const showLoginPwd  = ref(false)
const loginLoading  = ref(false)
const loginError    = ref('')

// 2FA
const needs2FA   = ref(false)
const twoFAChallenge = ref('')
const otpCode    = ref('')

// Recuperar contraseña
const showForgotPassword = ref(false)
const forgotIdentifier   = ref('')
const forgotLoading      = ref(false)
const forgotError        = ref('')
const forgotSent         = ref(false)

const onLogin = async () => {
  if (loginLoading.value) return
  loginLoading.value = true
  loginError.value = ''
  try {
    const data = await auth.login({ username: loginUsername.value, password: loginPassword.value })
    if (data?.requires_2fa) {
      twoFAChallenge.value = data.challenge
      needs2FA.value = true
      return
    }
    await carrito.cargar()
    emit('logged-in')
  } catch (err) {
    loginError.value = err.response?.status === 401 ? 'Usuario o contraseña incorrectos' : 'No se pudo iniciar sesión'
  } finally {
    loginLoading.value = false
  }
}

const onVerify2FA = async () => {
  if (loginLoading.value) return
  loginLoading.value = true
  loginError.value = ''
  try {
    await auth.loginWith2FA({ challenge: twoFAChallenge.value, otp: otpCode.value })
    await carrito.cargar()
    emit('logged-in')
  } catch (err) {
    loginError.value = err.response?.status === 401 || err.message ? (err.message || 'Código incorrecto') : 'No se pudo verificar'
  } finally {
    loginLoading.value = false
  }
}

const cancelar2FA = () => {
  needs2FA.value = false
  twoFAChallenge.value = ''
  otpCode.value = ''
  loginError.value = ''
}

const onForgotPassword = async () => {
  if (forgotLoading.value) return
  forgotError.value = ''
  forgotLoading.value = true
  try {
    await api.post('auth/password-reset/', { identifier: forgotIdentifier.value })
    forgotSent.value = true
  } catch {
    forgotError.value = 'No se pudo enviar el correo. Intenta de nuevo.'
  } finally {
    forgotLoading.value = false
  }
}

// ── Register ─────────────────────────────────────────────────────────────────
const registerUsername        = ref('')
const registerEmail           = ref('')
const registerPassword        = ref('')
const registerPasswordConfirm = ref('')
const showRegPwd              = ref(false)
const registerLoading         = ref(false)
const registerError           = ref('')
const registerMessage         = ref('')
const registerSuccess         = ref(false)
const regErr                  = ref({})

const pwdStrength = computed(() => {
  const p = registerPassword.value
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

const validarRegistro = () => {
  const e = {}
  if (!registerUsername.value.trim()) e.username = 'El usuario es obligatorio'
  else if (registerUsername.value.trim().length < 3) e.username = 'Mínimo 3 caracteres'
  if (!registerEmail.value.trim()) e.email = 'El correo es obligatorio'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerEmail.value)) e.email = 'Correo no válido'
  if (!registerPassword.value) e.password = 'La contraseña es obligatoria'
  else if (registerPassword.value.length < 8) e.password = 'Mínimo 8 caracteres'
  if (!registerPasswordConfirm.value) e.passwordConfirm = 'Confirma tu contraseña'
  else if (registerPassword.value !== registerPasswordConfirm.value) e.passwordConfirm = 'Las contraseñas no coinciden'
  regErr.value = e
  return Object.keys(e).length === 0
}

const onRegister = async () => {
  registerError.value = ''
  if (!validarRegistro()) return
  if (registerLoading.value) return
  registerLoading.value = true
  try {
    const { data } = await api.post('register/', {
      username: registerUsername.value.trim(),
      email: registerEmail.value.trim(),
      password: registerPassword.value,
    })
    registerMessage.value = data?.mensaje || 'Cuenta creada. Ya puedes iniciar sesión.'
    registerSuccess.value = true
  } catch (err) {
    const d = err.response?.data
    if (d?.username) registerError.value = Array.isArray(d.username) ? d.username[0] : d.username
    else if (d?.email) registerError.value = Array.isArray(d.email) ? d.email[0] : d.email
    else if (d?.password) registerError.value = Array.isArray(d.password) ? d.password[0] : d.password
    else registerError.value = 'No se pudo registrar la cuenta'
  } finally {
    registerLoading.value = false
  }
}
</script>
