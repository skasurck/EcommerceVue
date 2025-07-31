<template>
  <div class="flex items-center space-x-2">
    <input
      type="checkbox"
      :id="id"
      :checked="modelValue"
      @change="$emit('update:modelValue', $event.target.checked)"
    />
    <label :for="id">{{ label }}</label>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  label: String,
  id: String
})

const emit = defineEmits(['update:modelValue'])
</script>
