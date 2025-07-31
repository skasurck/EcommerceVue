<template>
  <div>
    <InputLabel :label="label" :required="required" />
    <select
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="w-full p-2 border rounded"
    >
      <option value="">Seleccione una opción</option>
      <option
        v-for="op in options"
        :key="optionValue ? op[optionValue] : op"
        :value="optionValue ? op[optionValue] : op"
      >
        {{ optionLabel ? op[optionLabel] : op }}
      </option>
    </select>
  </div>
</template>

<script setup>
import InputLabel from './InputLabel.vue'

defineProps({
  modelValue: [String, Number],
  label: String,
  required: Boolean,
  options: Array,
  optionLabel: String,
  optionValue: String
})
defineEmits(['update:modelValue'])
</script>
