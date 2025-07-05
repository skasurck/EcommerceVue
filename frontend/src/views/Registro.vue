<template>
  <div>
    <h2>Registro de usuario</h2>
    <form @submit.prevent="registrar">
      <input v-model="username" placeholder="Usuario" required />
      <input v-model="email" type="email" placeholder="Correo (opcional)" />
      <input v-model="password" type="password" placeholder="Contraseña" required />
      <button type="submit">Registrar</button>
    </form>
    <p v-if="mensaje" style="color: green">{{ mensaje }}</p>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../axios'

const username = ref('')
const email = ref('')
const password = ref('')
const mensaje = ref('')
const error = ref('')

const registrar = async () => {
  try {
    const res = await api.post('register/', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    mensaje.value = res.data.mensaje
    error.value = ''
    username.value = ''
    email.value = ''
    password.value = ''
  } catch (err) {
    console.error(err)
    mensaje.value = ''
    error.value = 'Error al registrar usuario'
  }
}
</script>
<style scoped>
 h2{
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
.error {
  color: red;
}
.success {
  color: green;
}
.formulario {
  max-width: 400px;
  margin: auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.formulario h2 {
  text-align: center;
}
.formulario div {
  margin-bottom: 15px;
}
.formulario label {
  display: block;
  margin-bottom: 5px;
}
.formulario input,
.formulario textarea {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
.formulario button {
  width: 100%;
  padding: 10px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.formulario button:hover {
  background-color: #218838;
}
.formulario p {
  text-align: center;
  margin-top: 10px;
}
.formulario p.error {
  color: red;
}
.formulario p.success {
  color: green;
}

</style>