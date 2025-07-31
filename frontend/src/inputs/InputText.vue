<template>
  <div>
    <InputLabel :label="label" :required="required" />
    <input
      type="text"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="w-full p-2 border rounded"
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
  error: String
})
defineEmits(['update:modelValue'])
</script>
