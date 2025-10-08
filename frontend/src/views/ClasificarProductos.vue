<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-slate-800">Clasificar productos con IA</h1>
      <button
        type="button"
        class="rounded bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:cursor-not-allowed disabled:bg-indigo-300"
        :disabled="loading"
        @click="classify"
      >
        <span v-if="!loading">Clasificar con IA</span>
        <span v-else>Clasificando…</span>
      </button>
    </div>

    <p class="text-sm text-slate-500">
      Se enviará una petición al backend para clasificar hasta 200 productos que no tengan etiqueta AI.
    </p>

    <div v-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <div v-if="results.length" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">ID</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Categoría Principal</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Subcategoría</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Confianza Principal</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Confianza Sub</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-200 bg-white">
          <tr v-for="item in results" :key="item.product_id">
            <td class="whitespace-nowrap px-4 py-2 text-sm text-slate-700">{{ item.product_id }}</td>
            <td class="whitespace-nowrap px-4 py-2 text-sm text-slate-700">{{ item.main || '—' }}</td>
            <td class="whitespace-nowrap px-4 py-2 text-sm text-slate-700">{{ item.sub || '—' }}</td>
            <td class="whitespace-nowrap px-4 py-2 text-sm text-slate-700">
              {{ formatConfidence(item.conf_main) }}
            </td>
            <td class="whitespace-nowrap px-4 py-2 text-sm text-slate-700">
              {{ formatConfidence(item.conf_sub) }}
            </td>
          </tr>
        </tbody>
      </table>
      <p class="mt-2 text-xs text-slate-500">Total clasificados: {{ results.length }}</p>
    </div>

    <div v-else-if="!loading" class="rounded border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
      Aún no hay resultados. Presiona el botón para comenzar.
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/axios'

const loading = ref(false)
const error = ref('')
const results = ref([])

const classify = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post('ai/classify-products/', {
      limit: 200,
      overwrite: false,
    })
    results.value = data?.results ?? []
  } catch (err) {
    const message = err?.response?.data?.detail || err?.message || 'No se pudo clasificar los productos.'
    error.value = message
  } finally {
    loading.value = false
  }
}

const formatConfidence = (value) => {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(1)}%`
}
</script>
