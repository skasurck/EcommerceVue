<template>
  <div class="relative" ref="containerRef">
    <div class="flex gap-2">
      <div class="relative flex-1">
        <input
          ref="inputRef"
          v-model="inputValue"
          @input="onInput"
          @focus="onFocus"
          @keydown.enter.prevent="selectFirst"
          @keydown.escape="close"
          @keydown.arrow-down.prevent="moveDown"
          @keydown.arrow-up.prevent="moveUp"
          type="text"
          :placeholder="placeholder"
          :class="inputClass"
          autocomplete="off"
        />
        <!-- Clear button -->
        <button
          v-if="inputValue"
          type="button"
          @click="clear"
          class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          tabindex="-1"
        >
          <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Suggestions dropdown -->
    <ul
      v-if="showSuggestions && filteredPaths.length"
      class="absolute z-50 mt-1 w-full overflow-auto rounded-lg border border-gray-200 bg-white shadow-xl"
      style="max-height: 260px"
    >
      <li
        v-for="(item, i) in filteredPaths"
        :key="item.finalId"
        @mousedown.prevent="selectItem(item)"
        @mouseover="activeIndex = i"
        class="flex cursor-pointer items-center gap-2 px-3 py-2 text-sm transition-colors"
        :class="i === activeIndex ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'"
      >
        <!-- Depth indicator -->
        <span class="shrink-0 rounded px-1.5 py-0.5 text-xs font-medium"
              :class="item.depth === 1 ? 'bg-blue-100 text-blue-600'
                    : item.depth === 2 ? 'bg-violet-100 text-violet-600'
                    : 'bg-emerald-100 text-emerald-600'">
          N{{ item.depth }}
        </span>
        <!-- Highlight matching text -->
        <span v-html="highlight(item.path)"></span>
      </li>
    </ul>

    <!-- No results -->
    <div
      v-else-if="showSuggestions && inputValue.length >= 2 && !filteredPaths.length"
      class="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-400 shadow-xl"
    >
      Sin resultados para "{{ inputValue }}"
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  categories: { type: Array, default: () => [] },
  // IDs actuales para sincronizar desde los dropdowns
  l1: { type: [Number, String], default: null },
  l2: { type: [Number, String], default: null },
  l3: { type: [Number, String], default: null },
  placeholder: { type: String, default: 'Escribe una ruta: Cómputo > Componentes > Gabinetes' },
  inputClass: {
    type: String,
    default: 'w-full rounded border border-gray-300 bg-white pr-7 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder:text-gray-400'
  },
})

const emit = defineEmits(['select'])

const inputRef = ref(null)
const containerRef = ref(null)
const inputValue = ref('')
const showSuggestions = ref(false)
const activeIndex = ref(-1)

// ── Build flat path list from tree ──────────────────────────────────────────
const allPaths = computed(() => {
  const result = []
  const traverse = (cats, prefix, l1Id, l2Id) => {
    for (const cat of cats) {
      const path = prefix ? `${prefix} > ${cat.nombre}` : cat.nombre
      const depth = l2Id ? 3 : l1Id ? 2 : 1
      const finalId = cat.id
      result.push({
        path,
        depth,
        finalId,
        l1Id: l1Id ?? cat.id,
        l2Id: l1Id ? (l2Id ?? cat.id) : null,
        l3Id: l2Id ? cat.id : null,
      })
      if (cat.subcategorias?.length) {
        traverse(cat.subcategorias, path, l1Id ?? cat.id, l1Id ? (l2Id ?? cat.id) : null)
      }
    }
  }
  traverse(props.categories, '', null, null)
  return result
})

// ── Filter ───────────────────────────────────────────────────────────────────
const filteredPaths = computed(() => {
  const q = inputValue.value.trim().toLowerCase()
  if (!q) return allPaths.value.slice(0, 25)
  return allPaths.value
    .filter(p => p.path.toLowerCase().includes(q))
    .slice(0, 20)
})

// ── Highlight matching text ──────────────────────────────────────────────────
const highlight = (text) => {
  const q = inputValue.value.trim()
  if (!q) return text
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark class="bg-yellow-100 text-yellow-800 rounded px-0.5">$1</mark>')
}

// ── Sync from parent dropdowns (when dropdowns change, update input text) ────
const buildPathFromIds = (l1, l2, l3) => {
  if (!l1) return ''
  const cat1 = allPaths.value.find(p => p.depth === 1 && p.l1Id === Number(l1))
  if (!cat1) return ''
  if (!l2) return cat1.path
  const cat2 = allPaths.value.find(p => p.depth === 2 && p.l1Id === Number(l1) && p.l2Id === Number(l2))
  if (!cat2) return cat1.path
  if (!l3) return cat2.path
  const cat3 = allPaths.value.find(p => p.depth === 3 && p.l1Id === Number(l1) && p.l2Id === Number(l2) && p.l3Id === Number(l3))
  return cat3 ? cat3.path : cat2.path
}

watch([() => props.l1, () => props.l2, () => props.l3], ([l1, l2, l3]) => {
  const path = buildPathFromIds(l1, l2, l3)
  if (path && path !== inputValue.value) inputValue.value = path
  if (!l1) inputValue.value = ''
}, { immediate: true })

// ── Events ───────────────────────────────────────────────────────────────────
const onInput = () => {
  showSuggestions.value = true
  activeIndex.value = -1
}

const onFocus = () => {
  showSuggestions.value = true
  activeIndex.value = -1
}

const close = () => {
  showSuggestions.value = false
  activeIndex.value = -1
}

const selectFirst = () => {
  const idx = activeIndex.value >= 0 ? activeIndex.value : 0
  if (filteredPaths.value[idx]) selectItem(filteredPaths.value[idx])
}

const moveDown = () => {
  if (activeIndex.value < filteredPaths.value.length - 1) activeIndex.value++
}

const moveUp = () => {
  if (activeIndex.value > 0) activeIndex.value--
}

const selectItem = (item) => {
  inputValue.value = item.path
  showSuggestions.value = false
  activeIndex.value = -1
  emit('select', {
    l1Id: item.l1Id,
    l2Id: item.l2Id,
    l3Id: item.l3Id,
    finalId: item.finalId,
    path: item.path,
  })
}

const clear = () => {
  inputValue.value = ''
  showSuggestions.value = false
  emit('select', { l1Id: null, l2Id: null, l3Id: null, finalId: null, path: '' })
  inputRef.value?.focus()
}

// ── Click outside to close ───────────────────────────────────────────────────
const onClickOutside = (e) => {
  if (containerRef.value && !containerRef.value.contains(e.target)) close()
}
onMounted(() => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))
</script>
