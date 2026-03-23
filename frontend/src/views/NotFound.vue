<template>
  <div class="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center">
    <p class="text-8xl font-black text-slate-200 dark:text-slate-800 select-none leading-none">404</p>
    <h1 class="mt-2 text-2xl font-semibold text-slate-800 dark:text-slate-100">Página no encontrada</h1>
    <p class="mt-2 text-slate-500 dark:text-slate-400 max-w-sm">
      La dirección que buscas no existe o fue movida.
    </p>
    <div class="mt-8 flex gap-3">
      <router-link
        to="/"
        class="rounded-full bg-slate-900 dark:bg-slate-100 px-5 py-2.5 text-sm font-semibold text-white dark:text-slate-900 hover:bg-slate-700 dark:hover:bg-slate-300 transition-colors"
      >
        Ir al inicio
      </router-link>
      <button
        type="button"
        class="rounded-full border border-slate-300 dark:border-slate-600 px-5 py-2.5 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        @click="router.back()"
      >
        Volver atrás
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>
