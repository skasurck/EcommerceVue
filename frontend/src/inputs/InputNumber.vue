<template>
  <div>
    <InputLabel :label="label" :error="error" :required="required" />
    <input
      :value="modelValue"
      @input="$emit('update:modelValue', parseFloat($event.target.value))"
      type="number"
      :step="step"
      :min="min"
      class="w-full p-2 border rounded"
      :class="{ 'border-red-500': error }"
    />
  </div>
</template>

<script setup>
import InputLabel from './InputLabel.vue'

defineProps({
  modelValue: Number,
  label: String,
  required: Boolean,
  error: String,
  step: { type: String, default: '0.01' },
  min: { type: Number, default: 0 }
})

defineEmits(['update:modelValue'])
</script>
