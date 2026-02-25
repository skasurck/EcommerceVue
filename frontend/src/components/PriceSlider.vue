<template>
  <div ref="slider"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import noUiSlider from 'nouislider'
import 'nouislider/dist/nouislider.css'

const props = defineProps({
  min: {
    type: Number,
    required: true,
  },
  max: {
    type: Number,
    required: true,
  },
  modelValue: {
    type: Array,
    required: true,
  },
})

const emits = defineEmits(['update:modelValue'])

const slider = ref(null)
let sliderInstance = null

const toSafeNumber = (value, fallback) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

const getRange = () => {
  let min = toSafeNumber(props.min, 0)
  let max = toSafeNumber(props.max, min)
  if (max < min) [min, max] = [max, min]
  return { min, max }
}

const getNormalizedModel = (range = getRange()) => {
  const values = Array.isArray(props.modelValue) ? props.modelValue : []
  let currentMin = toSafeNumber(values[0], range.min)
  let currentMax = toSafeNumber(values[1], range.max)

  currentMin = Math.min(Math.max(currentMin, range.min), range.max)
  currentMax = Math.min(Math.max(currentMax, range.min), range.max)
  if (currentMin > currentMax) [currentMin, currentMax] = [currentMax, currentMin]

  return [currentMin, currentMax]
}

const isSameValues = (a = [], b = []) => Math.abs((a[0] ?? 0) - (b[0] ?? 0)) < 0.01 && Math.abs((a[1] ?? 0) - (b[1] ?? 0)) < 0.01

const emitModelValue = (values = []) => {
  emits('update:modelValue', values.map((value) => toSafeNumber(parseFloat(value), 0)))
}

const createSlider = () => {
  if (!slider.value) return
  if (sliderInstance) {
    sliderInstance.destroy()
    sliderInstance = null
  }

  const range = getRange()
  const start = getNormalizedModel(range)

  sliderInstance = noUiSlider.create(slider.value, {
    start,
    connect: true,
    step: 1,
    range,
  })

  sliderInstance.on('update', emitModelValue)
}

const syncRange = () => {
  if (!sliderInstance) return
  const range = getRange()
  sliderInstance.updateOptions({ range }, false)
  sliderInstance.set(getNormalizedModel(range))
}

const syncModel = () => {
  if (!sliderInstance) return
  const nextValues = getNormalizedModel()
  const current = sliderInstance.get(true)
  const currentValues = Array.isArray(current) ? current.map((value) => toSafeNumber(value, 0)) : [toSafeNumber(current, 0), toSafeNumber(current, 0)]
  if (isSameValues(currentValues, nextValues)) return
  sliderInstance.set(nextValues)
}

onMounted(() => {
  createSlider()
})

watch(
  () => [props.min, props.max],
  () => {
    if (!sliderInstance) {
      createSlider()
      return
    }
    syncRange()
  },
)

watch(
  () => props.modelValue,
  () => {
    syncModel()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  if (!sliderInstance) return
  sliderInstance.destroy()
  sliderInstance = null
})
</script>
