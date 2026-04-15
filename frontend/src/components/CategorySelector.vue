<template>
  <div>
    <InputLabel :label="label" />
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <SelectInput
        v-model="selectedLevel1"
        :options="level1Options"
        label="Categoría Nivel 1"
        option-value="id"
        option-label="nombre"
      />
      <SelectInput
        v-if="level2Options.length"
        v-model="selectedLevel2"
        :options="level2Options"
        label="Categoría Nivel 2"
        option-value="id"
        option-label="nombre"
      />
      <SelectInput
        v-if="level3Options.length"
        v-model="selectedLevel3"
        :options="level3Options"
        label="Categoría Nivel 3"
        option-value="id"
        option-label="nombre"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue';
import { getCategorias } from '@/api/productos.js';
import SelectInput from '@/inputs/SelectInput.vue';
import InputLabel from '@/inputs/InputLabel.vue';

export default {
  name: 'CategorySelector',
  components: { SelectInput, InputLabel },
  props: {
    modelValue: {
      type: Array,
      default: () => [],
    },
    label: {
      type: String,
      default: 'Categorías',
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const allCategories = ref([]);
    const selectedLevel1 = ref(null);
    const selectedLevel2 = ref(null);
    const selectedLevel3 = ref(null);
    
    // Flag to prevent watchers from running during initial setup
    const isInitializing = ref(true);

    const level1Options = computed(() => allCategories.value.filter(c => c.parent === null));
    
    const level2Options = computed(() => {
        const sel1 = Number(selectedLevel1.value);
        return sel1 ? allCategories.value.filter(c => c.parent === sel1) : [];
    });

    const level3Options = computed(() => {
        const sel2 = Number(selectedLevel2.value);
        return sel2 ? allCategories.value.filter(c => c.parent === sel2) : [];
    });

    const findCategoryById = (id) => allCategories.value.find(c => c.id === id);

    const setInitialSelection = () => {
      if (props.modelValue && props.modelValue.length > 0 && allCategories.value.length > 0) {
        const selectedId = props.modelValue[0];
        const selectedCategory = findCategoryById(selectedId);

        if (selectedCategory) {
          const path = [];
          let current = selectedCategory;
          while(current) {
            path.unshift(current);
            current = current.parent ? findCategoryById(current.parent) : null;
          }

          if (path.length > 0) selectedLevel1.value = path[0]?.id || null;
          if (path.length > 1) selectedLevel2.value = path[1]?.id || null;
          if (path.length > 2) selectedLevel3.value = path[2]?.id || null;
        }
      }
       // Allow watchers to run after initialization is complete
      setTimeout(() => {
        isInitializing.value = false;
      }, 0);
    };

    onMounted(async () => {
      try {
        const response = await getCategorias();
        allCategories.value = response.data;
        setInitialSelection();
      } catch (error) {
        console.error('Error al cargar las categorías:', error);
      }
    });

    watch(() => props.modelValue, () => {
      isInitializing.value = true;
      setInitialSelection();
    }, { deep: true });

    const updateSelection = () => {
      // No emitir mientras se está inicializando para evitar el ciclo reactivo:
      // setInitialSelection → watcher selectedLevel → updateSelection → emit →
      // parent actualiza form.categorias (nueva referencia) → watcher modelValue → loop
      if (isInitializing.value) return;

      const selection = [];
      if (selectedLevel3.value) {
        selection.push(Number(selectedLevel3.value));
      } else if (selectedLevel2.value) {
        selection.push(Number(selectedLevel2.value));
      } else if (selectedLevel1.value) {
        selection.push(Number(selectedLevel1.value));
      }

      // Evitar emitir si el contenido es idéntico al actual (previene renders innecesarios)
      const current = props.modelValue ?? [];
      if (selection.length === current.length && selection.every((v, i) => v === current[i])) return;

      emit('update:modelValue', selection);
    };

    watch(selectedLevel1, (newValue, oldValue) => {
      if (!isInitializing.value && newValue !== oldValue) {
        selectedLevel2.value = null;
        selectedLevel3.value = null;
      }
      updateSelection();
    });

    watch(selectedLevel2, (newValue, oldValue) => {
      if (!isInitializing.value && newValue !== oldValue) {
        selectedLevel3.value = null;
      }
      updateSelection();
    });

    watch(selectedLevel3, () => {
        updateSelection();
    });

    return {
      selectedLevel1,
      selectedLevel2,
      selectedLevel3,
      level1Options,
      level2Options,
      level3Options,
    };
  },
};
</script>
