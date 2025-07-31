<template>
  <label class="block text-sm font-medium mb-1">
    {{ label }}
    <span v-if="required" class="text-red-500">*</span>
    <span v-if="error" class="text-red-500 text-xs block">{{ error }}</span>
  </label>
</template>

<script setup>
defineProps({
  label: String,
  required: Boolean,
  error: String
})
</script>
