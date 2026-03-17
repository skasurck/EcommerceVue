<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-slate-800">Estadisticas de aprendizaje IA</h1>
      <button
        type="button"
        class="rounded bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
        :disabled="loading"
        @click="loadStats"
      >
        {{ loading ? 'Cargando...' : 'Actualizar' }}
      </button>
    </div>

    <div v-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <article class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Feedback total</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">{{ summary.total_feedback }}</p>
      </article>
      <article class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Ultimos 7 dias</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">{{ summary.feedback_last_7_days }}</p>
      </article>
      <article class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Ultimos 30 dias</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">{{ summary.feedback_last_30_days }}</p>
      </article>
      <article class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Productos unicos</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">{{ summary.unique_products }}</p>
      </article>
      <article class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Subcategorias unicas</p>
        <p class="mt-2 text-2xl font-semibold text-slate-800">{{ summary.unique_subcategories }}</p>
      </article>
      <article class="rounded-lg border border-slate-200 bg-white p-4">
        <p class="text-xs uppercase tracking-wide text-slate-500">Modelo listo</p>
        <p class="mt-2 text-2xl font-semibold" :class="model.is_ready ? 'text-emerald-600' : 'text-amber-600'">
          {{ model.is_ready ? 'Si' : 'No' }}
        </p>
        <p class="mt-1 text-xs text-slate-500">
          muestras: {{ model.total_samples }} | etiquetas: {{ model.labels }}
        </p>
      </article>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <section class="rounded-lg border border-slate-200 bg-white p-4">
        <h2 class="text-sm font-semibold text-slate-700">Feedback por origen</h2>
        <div class="mt-3 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-3 py-2 text-left font-medium text-slate-500">Origen</th>
                <th class="px-3 py-2 text-left font-medium text-slate-500">Total</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
              <tr v-for="item in bySource" :key="item.source">
                <td class="px-3 py-2 text-slate-700">{{ item.source }}</td>
                <td class="px-3 py-2 text-slate-700">{{ item.total }}</td>
              </tr>
              <tr v-if="!bySource.length">
                <td colspan="2" class="px-3 py-4 text-center text-slate-500">Sin datos</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="rounded-lg border border-slate-200 bg-white p-4">
        <h2 class="text-sm font-semibold text-slate-700">Top subcategorias</h2>
        <div class="mt-3 overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-3 py-2 text-left font-medium text-slate-500">Subcategoria</th>
                <th class="px-3 py-2 text-left font-medium text-slate-500">Total</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
              <tr v-for="item in topSubcategories" :key="item.target_sub">
                <td class="px-3 py-2 text-slate-700">{{ item.target_sub }}</td>
                <td class="px-3 py-2 text-slate-700">{{ item.total }}</td>
              </tr>
              <tr v-if="!topSubcategories.length">
                <td colspan="2" class="px-3 py-4 text-center text-slate-500">Sin datos</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '@/axios'

const loading = ref(false)
const error = ref('')
const summary = ref({
  total_feedback: 0,
  feedback_last_7_days: 0,
  feedback_last_30_days: 0,
  unique_products: 0,
  unique_subcategories: 0,
})
const model = ref({
  is_ready: false,
  total_samples: 0,
  labels: 0,
})
const bySource = ref([])
const topSubcategories = ref([])

const loadStats = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('ai/learning-stats/')
    summary.value = { ...summary.value, ...(data?.summary || {}) }
    model.value = { ...model.value, ...(data?.model || {}) }
    bySource.value = Array.isArray(data?.by_source) ? data.by_source : []
    topSubcategories.value = Array.isArray(data?.top_subcategories) ? data.top_subcategories : []
  } catch (err) {
    const status = err?.response?.status
    if (status === 403) {
      error.value = 'No tienes permisos para ver estas estadisticas.'
    } else {
      error.value = err?.response?.data?.detail || 'No se pudieron cargar las estadisticas.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>
