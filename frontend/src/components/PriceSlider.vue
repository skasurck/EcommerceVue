<template>
  <div ref="slider"></div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import noUiSlider from 'nouislider';
import 'nouislider/dist/nouislider.css';

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
});

const emits = defineEmits(['update:modelValue']);

const slider = ref(null);

onMounted(() => {
  const sliderInstance = noUiSlider.create(slider.value, {
    start: props.modelValue,
    connect: true,
    range: {
      min: props.min,
      max: props.max,
    },
  });

  sliderInstance.on('update', (values) => {
    emits('update:modelValue', values.map(v => parseFloat(v)));
  });
});
</script>
