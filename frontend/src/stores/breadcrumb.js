import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useBreadcrumbStore = defineStore('breadcrumb', () => {
  const dynamicLabel = ref('')

  function setLabel(label) {
    dynamicLabel.value = label
  }

  function clear() {
    dynamicLabel.value = ''
  }

  return { dynamicLabel, setLabel, clear }
})
