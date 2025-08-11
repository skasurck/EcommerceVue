<template>
  <div class="max-w-lg mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold mb-4">Inicio de sesión y seguridad</h1>
    <section class="bg-white border rounded-lg p-5">
      <h2 class="text-xl font-semibold mb-3">Cambiar contraseña</h2>
      <form @submit.prevent="enviar" class="grid grid-cols-1 gap-3">
        <input v-model="form.old_password" type="password" placeholder="Contraseña actual" class="border p-2 rounded" />
        <input v-model="form.new_password" type="password" placeholder="Nueva contraseña" class="border p-2 rounded" />
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">Guardar</button>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { cambiarPassword } from '@/services/account'
const form = ref({ old_password: '', new_password: '' })
const enviar = async () => {
  await cambiarPassword(form.value)
  form.value = { old_password: '', new_password: '' }
}
</script>
