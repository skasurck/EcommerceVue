<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-semibold text-slate-800">Clasificar productos con IA</h1>
      <button
        type="button"
        class="rounded bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:cursor-not-allowed disabled:bg-indigo-300"
        :disabled="loading"
        @click="startClassification"
      >
        <span v-if="!loading">Clasificar con IA</span>
        <span v-else>Clasificando…</span>
      </button>
    </div>

    <!-- Opciones de Clasificación -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 border rounded-md">
      <InputNumber
        v-model="limit"
        label="Número de productos a analizar"
        :disabled="loading"
      />
      <SwitchInput
        v-model="overwrite"
        label="Re-clasificar productos"
        description="Si se activa, se volverán a clasificar productos aunque ya tengan una categoría."
        :disabled="loading"
      />
      <SwitchInput
        v-model="ignoreTimeLimit"
        label="Ignorar límite de 10 días"
        description="Incluir productos clasificados recientemente (en los últimos 10 días)."
        :disabled="loading"
      />
    </div>

    <!-- Info sobre auto-aprobación -->
    <div class="rounded-md border border-blue-100 bg-blue-50 p-4 text-sm text-blue-800">
      <p class="font-medium mb-1">¿Cómo funciona la auto-clasificación?</p>
      <p>Los productos donde Claude tiene <strong>85% o más de confianza</strong> se clasifican automáticamente sin revisión. Los demás aparecen en "Revisar clasificaciones" para que los apruebes manualmente.</p>
    </div>

    <!-- Progreso y Estado -->
    <div v-if="loading" class="space-y-3">
      <div class="flex items-center justify-between text-sm font-medium text-slate-600">
        <span>Procesando… ({{ progress.current || 0 }} de {{ progress.total || 0 }})</span>
        <span>{{ progressPercentage.toFixed(0) }}%</span>
      </div>
      <div class="w-full bg-slate-200 rounded-full h-2.5">
        <div class="bg-indigo-600 h-2.5 rounded-full transition-all duration-500" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <!-- Contadores en tiempo real -->
      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-md border border-green-200 bg-green-50 p-3 text-center">
          <p class="text-2xl font-bold text-green-700">{{ progress.auto_applied || 0 }}</p>
          <p class="text-xs text-green-600">Auto-aplicados ✓</p>
        </div>
        <div class="rounded-md border border-amber-200 bg-amber-50 p-3 text-center">
          <p class="text-2xl font-bold text-amber-700">{{ progress.pending_review || 0 }}</p>
          <p class="text-xs text-amber-600">Pendientes de revisión</p>
        </div>
      </div>
      <p v-if="progress.status" class="text-xs text-slate-500 truncate">{{ progress.status }}</p>
    </div>

    <p v-if="!loading" class="text-sm text-slate-500">
      La clasificación se ejecuta en segundo plano. Puedes cerrar esta página y volver más tarde si lo deseas.
    </p>

    <!-- Errores -->
    <div v-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Resultados finales -->
    <div v-if="lastResult" class="space-y-4">
      <h2 class="text-lg font-semibold text-slate-800">Resultado de la última ejecución</h2>
      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-lg border border-green-200 bg-green-50 p-5 text-center">
          <p class="text-3xl font-bold text-green-700">{{ lastResult.auto_applied || 0 }}</p>
          <p class="mt-1 text-sm text-green-600 font-medium">Clasificados automáticamente</p>
          <p class="text-xs text-green-500 mt-1">Confianza ≥ 85%</p>
        </div>
        <div class="rounded-lg border border-amber-200 bg-amber-50 p-5 text-center">
          <p class="text-3xl font-bold text-amber-700">{{ lastResult.pending_review || 0 }}</p>
          <p class="mt-1 text-sm text-amber-600 font-medium">Pendientes de revisión</p>
          <p class="text-xs text-amber-500 mt-1">Confianza &lt; 85%</p>
        </div>
      </div>
      <p v-if="lastResult.pending_review > 0" class="text-sm text-slate-600">
        Ve a <strong>Revisar clasificaciones</strong> para aprobar los productos pendientes.
      </p>
    </div>

    <div v-else-if="!loading" class="rounded border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500">
      Aún no hay resultados. Presiona el botón para comenzar.
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/axios'
import InputNumber from '@/inputs/InputNumber.vue'
import SwitchInput from '@/inputs/SwitchInput.vue'

const loading = ref(false)
const error = ref('')
const lastResult = ref(null)
const limit = ref(100)
const overwrite = ref(false)
const ignoreTimeLimit = ref(false)
const taskId = ref(null)
const progress = ref({})
let pollingInterval = null

const LS_TASK_ID_KEY = 'classification_task_id'

const progressPercentage = computed(() => {
  if (!progress.value.total || progress.value.total === 0) return 0
  return (progress.value.current / progress.value.total) * 100
})

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  localStorage.removeItem(LS_TASK_ID_KEY)
  taskId.value = null
  loading.value = false
}

const pollTaskStatus = async () => {
  if (!taskId.value) return
  try {
    const { data } = await api.get(`ai/classify-products/status/${taskId.value}/`)
    progress.value = data.info || {}

    if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
      stopPolling()
      if (data.status === 'SUCCESS') {
        lastResult.value = data.result || {}
        error.value = ''
      } else {
        error.value = `La tarea falló: ${data.info}`
      }
    }
  } catch {
    stopPolling()
    error.value = 'Error al consultar el estado de la tarea. La tarea puede haber expirado o sido inválida.'
  }
}

const startClassification = async () => {
  loading.value = true
  error.value = ''
  lastResult.value = null
  progress.value = {}

  try {
    const { data } = await api.post('ai/classify-products/', {
      limit: Number(limit.value),
      overwrite: overwrite.value,
      ignore_time_limit: ignoreTimeLimit.value,
    })

    if (data.task_id) {
      taskId.value = data.task_id
      localStorage.setItem(LS_TASK_ID_KEY, taskId.value)
      pollingInterval = setInterval(pollTaskStatus, 3000)
    } else {
      loading.value = false
      error.value = data.message || 'No se pudo iniciar la tarea de clasificación.'
    }
  } catch (err) {
    error.value = err?.response?.data?.detail || err?.message || 'No se pudo iniciar la clasificación.'
    loading.value = false
  }
}

onMounted(() => {
  const savedTaskId = localStorage.getItem(LS_TASK_ID_KEY)
  if (savedTaskId) {
    taskId.value = savedTaskId
    loading.value = true
    pollTaskStatus()
    pollingInterval = setInterval(pollTaskStatus, 3000)
  }
})
</script>
