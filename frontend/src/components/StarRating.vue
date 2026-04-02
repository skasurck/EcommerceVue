<template>
  <!-- Modo interactivo (para escribir una reseña) -->
  <div v-if="interactive" class="flex gap-1">
    <button
      v-for="n in 5"
      :key="n"
      type="button"
      @click="emit('update:modelValue', n)"
      @mouseenter="hovered = n"
      @mouseleave="hovered = 0"
      class="focus:outline-none"
      :aria-label="`${n} estrella${n > 1 ? 's' : ''}`"
    >
      <svg
        viewBox="0 0 20 20"
        :class="[sizeClass, n <= (hovered || modelValue) ? 'text-amber-400' : 'text-slate-300']"
        fill="currentColor"
      >
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.958a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.447a1 1 0 00-1.175 0l-3.37 2.447c-.784.57-1.838-.196-1.54-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.385c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69L9.049 2.927z"/>
      </svg>
    </button>
  </div>

  <!-- Modo display (mostrar rating) -->
  <div v-else class="flex items-center gap-1">
    <div class="flex">
      <svg
        v-for="n in 5"
        :key="n"
        viewBox="0 0 20 20"
        :class="[sizeClass, starColor(n)]"
        fill="currentColor"
      >
        <defs v-if="isHalf(n)">
          <linearGradient :id="`half-${uid}-${n}`" x1="0" x2="1" y1="0" y2="0">
            <stop offset="50%" stop-color="currentColor" class="text-amber-400" style="color:#fbbf24"/>
            <stop offset="50%" stop-color="currentColor" class="text-slate-300" style="color:#cbd5e1"/>
          </linearGradient>
        </defs>
        <path
          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.958a1 1 0 00.95.69h4.162c.969 0 1.371 1.24.588 1.81l-3.37 2.448a1 1 0 00-.364 1.118l1.287 3.957c.3.922-.755 1.688-1.54 1.118l-3.37-2.447a1 1 0 00-1.175 0l-3.37 2.447c-.784.57-1.838-.196-1.54-1.118l1.287-3.957a1 1 0 00-.364-1.118L2.063 9.385c-.783-.57-.38-1.81.588-1.81h4.162a1 1 0 00.95-.69L9.049 2.927z"
          :fill="isHalf(n) ? `url(#half-${uid}-${n})` : 'currentColor'"
        />
      </svg>
    </div>
    <span v-if="showCount && count !== undefined" class="text-slate-500 text-xs leading-none">
      ({{ count }})
    </span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },      // para modo interactivo
  rating: { type: Number, default: 0 },           // para modo display
  count: { type: Number, default: undefined },
  size: { type: String, default: 'md' },          // sm | md | lg
  interactive: { type: Boolean, default: false },
  showCount: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue'])

const hovered = ref(0)
const uid = Math.random().toString(36).slice(2, 7)

const sizeClass = computed(() => ({
  sm: 'h-3.5 w-3.5',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
}[props.size] ?? 'h-5 w-5'))

const isHalf = (n) => {
  const r = props.rating
  return r < n && r > n - 1
}

const starColor = (n) => {
  if (isHalf(n)) return 'text-transparent'   // usa gradient fill
  if (n <= Math.round(props.rating)) return 'text-amber-400'
  return 'text-slate-300'
}
</script>
