<template>
  <div class="p-6 bg-white rounded-lg shadow-md">
    <h2 class="text-2xl font-semibold text-slate-800 mb-4">Gestión de Promociones</h2>

    <div class="space-y-6">
      <!-- Sección de Ofertas Diarias -->
      <div>
        <h3 class="text-lg font-medium text-slate-700">Ofertas Diarias Automáticas</h3>
        <p class="text-sm text-slate-500 mt-1">
          Activa o desactiva la creación automática de ofertas diarias. Cada día, el sistema seleccionará 10 productos al azar y les aplicará un 5% de descuento.
        </p>

        <div class="mt-4 flex items-center">
          <SwitchInput 
            :modelValue="settings.daily_offers_enabled"
            @update:modelValue="updateSettings"
          />
          <span class="ml-4 text-sm font-medium"
            :class="settings.daily_offers_enabled ? 'text-emerald-600' : 'text-slate-500'">
            {{ settings.daily_offers_enabled ? 'Activado' : 'Desactivado' }}
          </span>
        </div>
      </div>

      <!-- Sección para ejecutar manualmente -->
      <div class="border-t pt-6">
        <h3 class="text-lg font-medium text-slate-700">Ejecución Manual</h3>
        <p class="text-sm text-slate-500 mt-1">
          Si las ofertas automáticas están activadas, puedes forzar la creación de un nuevo set de ofertas para hoy. Esto desactivará las ofertas actuales y generará unas nuevas.
        </p>
        <button 
          @click="runManually"
          :disabled="!settings.daily_offers_enabled || isLoadingManualRun"
          class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md shadow-sm hover:bg-indigo-700 disabled:bg-slate-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          <span v-if="isLoadingManualRun">Ejecutando...</span>
          <span v-else>Generar Ofertas Ahora</span>
        </button>
        <p v-if="manualRunMessage" class="text-sm mt-2" :class="manualRunError ? 'text-red-500' : 'text-emerald-600'">
          {{ manualRunMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SwitchInput from '@/inputs/SwitchInput.vue';
import api from '@/axios'; // Importar la instancia de axios configurada

const settings = ref({
  daily_offers_enabled: false
});

const isLoading = ref(true);
const isLoadingManualRun = ref(false);
const manualRunMessage = ref('');
const manualRunError = ref(false);

// Fetch initial settings
onMounted(async () => {
  try {
    isLoading.value = true;
    const response = await api.get('promotions/settings/');
    settings.value = response.data;
  } catch (error) {
    console.error('Error fetching promotion settings:', error);
    // podrías mostrar una notificación al usuario
  } finally {
    isLoading.value = false;
  }
});

// Update settings when toggle is clicked
const updateSettings = async (newValue) => {
  const oldValue = settings.value.daily_offers_enabled;
  settings.value.daily_offers_enabled = newValue;

  try {
    await api.patch('promotions/settings/', {
      daily_offers_enabled: newValue
    });
    // podrías mostrar una notificación de éxito
  } catch (error) {
    console.error('Error updating promotion settings:', error);
    settings.value.daily_offers_enabled = oldValue; // Revert on error
    // podrías mostrar una notificación de error
  }
};

const runManually = async () => {
  isLoadingManualRun.value = true;
  manualRunMessage.value = '';
  manualRunError.value = false;

  try {
    const response = await api.post('promotions/run-daily-offers/');
    manualRunMessage.value = response.data.output || 'Comando ejecutado con éxito.';
  } catch (error) {
    console.error('Error running daily offers command:', error);
    manualRunMessage.value = error.response?.data?.message || 'Ocurrió un error al ejecutar el comando.';
    manualRunError.value = true;
  } finally {
    isLoadingManualRun.value = false;
  }
};

</script>
