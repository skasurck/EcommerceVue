<template>
  <ul class="space-y-1">
    <li v-for="categoria in categorias" :key="categoria.id">
      <div class="flex items-center gap-2">
        <button
          v-if="hasChildren(categoria)"
          type="button"
          class="h-5 w-5 rounded text-gray-500 hover:bg-gray-100"
          @click="toggleExpand(categoria.id)"
          :aria-label="isExpanded(categoria.id) ? 'Contraer categoría' : 'Expandir categoría'"
        >
          {{ isExpanded(categoria.id) ? '▾' : '▸' }}
        </button>
        <span v-else class="inline-block h-5 w-5"></span>

        <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
          <input
            type="radio"
            :name="groupName"
            :value="categoria.id"
            :checked="isSelected(categoria.id)"
            class="text-blue-600 focus:ring-blue-500"
            @change="selectCategoria(categoria.id)"
          />
          <span>{{ categoria.nombre }}</span>
          <span
            v-if="Number.isFinite(Number(categoria.total_productos))"
            class="text-xs text-gray-500"
          >
            ({{ Number(categoria.total_productos) }})
          </span>
        </label>
      </div>

      <div
        v-if="hasChildren(categoria) && isExpanded(categoria.id)"
        class="ml-5 border-l border-gray-200 pl-2 mt-1"
      >
        <CategoryTreeRadio
          :categorias="categoria.children"
          :selected-categoria="selectedCategoria"
          :expanded-ids="expandedIds"
          :group-name="groupName"
          @update:selectedCategoria="$emit('update:selectedCategoria', $event)"
          @update:expandedIds="$emit('update:expandedIds', $event)"
          @select="$emit('select')"
        />
      </div>
    </li>
  </ul>
</template>

<script setup>
defineOptions({ name: 'CategoryTreeRadio' })

const props = defineProps({
  categorias: {
    type: Array,
    required: true,
  },
  selectedCategoria: {
    type: [String, Number],
    default: '',
  },
  expandedIds: {
    type: Array,
    default: () => [],
  },
  groupName: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:selectedCategoria', 'update:expandedIds', 'select'])

const hasChildren = (categoria) => Array.isArray(categoria?.children) && categoria.children.length > 0

const isExpanded = (id) => props.expandedIds.some((item) => String(item) === String(id))

const toggleExpand = (id) => {
  const key = String(id)
  const exists = props.expandedIds.some((item) => String(item) === key)
  if (exists) {
    emit(
      'update:expandedIds',
      props.expandedIds.filter((item) => String(item) !== key),
    )
    return
  }
  emit('update:expandedIds', [...props.expandedIds, id])
}

const isSelected = (id) => String(props.selectedCategoria ?? '') === String(id)

const selectCategoria = (id) => {
  emit('update:selectedCategoria', id)
  emit('select')
}
</script>
