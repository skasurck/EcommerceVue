<script setup>
import { Icon } from "@iconify/vue"
const props = defineProps({
  title: { type: String, required: true },
  desc:  { type: String, default: "" },
  icon:  { type: String, default: "mdi:account" },
  to:    { type: String, default: "" }, // ruta o vacío
})
</script>

<template>
  <component
    :is="to ? 'RouterLink' : 'div'"
    :to="to || undefined"
    class="block bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition
           hover:border-gray-300"
  >
    <div class="flex items-start gap-4">
      <div class="shrink-0 grid place-items-center w-14 h-14 rounded-full bg-gray-50 border">
        <Icon :icon="icon" class="text-2xl text-gray-600" />
      </div>
      <div>
        <h3 class="text-[17px] font-semibold text-gray-900 leading-tight">{{ title }}</h3>
        <p class="mt-1 text-sm text-gray-600">{{ desc }}</p>
      </div>
    </div>
  </component>
</template>
