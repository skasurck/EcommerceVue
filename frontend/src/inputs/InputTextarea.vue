<template>
  <div>
    <InputLabel :label="label" :error="error" :required="required" />
    <textarea
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :rows="rows"
      class="w-full p-2 border rounded resize-none"
      :class="{ 'border-red-500': error }"
    />
  </div>
</template>

<script setup>
import InputLabel from './InputLabel.vue'

defineProps({
  modelValue: String,
  label: String,
  required: Boolean,
  error: String,
  rows: { type: Number, default: 3 }
})

defineEmits(['update:modelValue'])
</script>
