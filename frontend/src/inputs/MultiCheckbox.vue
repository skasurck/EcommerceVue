<template>
  <div>
    <InputLabel :label="label" />
    <div v-for="opt in options" :key="opt[optionValue]" class="mt-1">
      <label>
        <input type="checkbox" :value="opt[optionValue]" v-model="selected" />
        {{ opt[optionLabel] }}
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import InputLabel from './InputLabel.vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  label: String,
  options: { type: Array, default: () => [] },
  optionLabel: { type: String, default: 'label' },
  optionValue: { type: String, default: 'value' }
})

const emit = defineEmits(['update:modelValue'])
const selected = ref([...props.modelValue])

watch(selected, val => emit('update:modelValue', val), { deep: true })
</script>
