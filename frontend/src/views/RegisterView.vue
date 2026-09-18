<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(username.value, email.value, password.value)
    router.push('/')
  } catch (e) {
    // FastAPI отдаёт ошибку в e.response.data.detail
    error.value = e.response?.data?.detail || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-sm mx-auto mt-16 bg-gray-800 p-8 rounded-lg shadow-lg">
    <h1 class="text-2xl font-bold mb-6 text-center">Регистрация</h1>
    <div v-if="error" class="mb-4 text-sm text-red-400 bg-red-900/30 p-2 rounded">{{ error }}</div>
    <div class="space-y-4">
      <input v-model="username" placeholder="Имя пользователя"
        class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500" />
      <input v-model="email" type="email" placeholder="Email (необязательно)"
        class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500" />
      <input v-model="password" type="password" placeholder="Пароль" @keyup.enter="handleRegister"
        class="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500" />
      <button @click="handleRegister" :disabled="loading"
        class="w-full bg-emerald-600 text-white py-2 rounded hover:bg-emerald-700 disabled:opacity-50">
        {{ loading ? 'Создание...' : 'Зарегистрироваться' }}
      </button>
    </div>
    <p class="mt-4 text-sm text-center text-gray-400">
      Уже есть аккаунт? <RouterLink to="/login" class="text-emerald-400">Войти</RouterLink>
    </p>
  </div>
</template>