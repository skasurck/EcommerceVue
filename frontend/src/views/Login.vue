<template>
  <div>
    <h2>Iniciar sesión</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Usuario" required />
      <input v-model="password" type="password" placeholder="Contraseña" required />
      <button type="submit">Entrar</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../axios'

const username = ref('')
const password = ref('')
const error = ref('')

const login = async () => {
  try {
    const res = await api.post('/token/', {
      username: username.value,
      password: password.value
    })
    localStorage.setItem('access', res.data.access)
    localStorage.setItem('refresh', res.data.refresh)
    error.value = ''
    alert('Login exitoso')
  } catch (err) {
    console.error(err)
    error.value = 'Credenciales inválidas'
  }
}
</script>
<style scoped>
h2 {
  text-align: center;
  margin-bottom: 20px;
}
form {
  display: flex;
  flex-direction: column;
  max-width: 300px;
  margin: auto;
}
input {
  margin-bottom: 10px;
  padding: 8px;
  font-size: 16px;
}
button {
  padding: 10px;
  font-size: 16px;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background-color: #0056b3;
}
p {
  text-align: center;
  margin-top: 10px;
}

</style>