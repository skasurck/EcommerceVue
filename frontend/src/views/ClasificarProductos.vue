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

    <!-- Progreso y Estado -->
    <div v-if="loading" class="space-y-2">
        <p class="text-sm font-medium text-slate-600">Procesando... ({{ progress.current || 0 }} de {{ progress.total || 0 }})</p>
        <div class="w-full bg-slate-200 rounded-full h-2.5">
            <div class="bg-indigo-600 h-2.5 rounded-full" :style="{ width: progressPercentage + '%' }"></div>
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

    <!-- Resultados -->
    <div v-if="results.length" class="overflow-x-auto">
      <h2 class="text-lg font-semibold text-slate-800 mb-2">Resultados de la última ejecución</h2>
      <table class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">ID</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Categoría Principal</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Subcategoría</th>
            <th scope="col" class="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Confianza</th>
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
import { ref, computed, onMounted } from 'vue'
import api from '@/axios'
import InputNumber from '@/inputs/InputNumber.vue'
import SwitchInput from '@/inputs/SwitchInput.vue'

const loading = ref(false)
const error = ref('')
const results = ref([])
const limit = ref(100);
const overwrite = ref(false);
const ignoreTimeLimit = ref(false);
const taskId = ref(null);
const progress = ref({});
let pollingInterval = null;

const LS_TASK_ID_KEY = 'classification_task_id';

const progressPercentage = computed(() => {
    if (!progress.value.total || progress.value.total === 0) return 0;
    return (progress.value.current / progress.value.total) * 100;
});

const stopPolling = () => {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
    localStorage.removeItem(LS_TASK_ID_KEY);
    taskId.value = null;
    loading.value = false;
};

const pollTaskStatus = async () => {
    if (!taskId.value) return;

    try {
        const { data } = await api.get(`ai/classify-products/status/${taskId.value}/`);
        progress.value = data.info || {};

        if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
            stopPolling();
            if (data.status === 'SUCCESS') {
                results.value = data.result || [];
                error.value = '';
            } else {
                error.value = `La tarea falló: ${data.info}`;
            }
        }
    } catch (err) {
        stopPolling();
        error.value = 'Error al consultar el estado de la tarea. La tarea puede haber expirado o sido inválida.';
    }
};

const startClassification = async () => {
  loading.value = true;
  error.value = '';
  results.value = [];
  progress.value = {};

  try {
    const { data } = await api.post('ai/classify-products/', {
        limit: Number(limit.value),
        overwrite: overwrite.value,
        ignore_time_limit: ignoreTimeLimit.value,
    });
    
    if (data.task_id) {
        taskId.value = data.task_id;
        localStorage.setItem(LS_TASK_ID_KEY, taskId.value);
        pollingInterval = setInterval(pollTaskStatus, 3000);
    } else {
        loading.value = false;
        error.value = data.message || "No se pudo iniciar la tarea de clasificación.";
    }

  } catch (err) {
    const message = err?.response?.data?.detail || err?.message || 'No se pudo iniciar la clasificación.';
    error.value = message;
    loading.value = false;
  }
}

onMounted(() => {
    const savedTaskId = localStorage.getItem(LS_TASK_ID_KEY);
    if (savedTaskId) {
        taskId.value = savedTaskId;
        loading.value = true;
        pollTaskStatus(); // Llama una vez inmediatamente para obtener el estado actual
        pollingInterval = setInterval(pollTaskStatus, 3000);
    }
});

const formatConfidence = (value) => {
  if (value === null || value === undefined) return '—'
  return `${(value * 100).toFixed(1)}%`
}
</script>
