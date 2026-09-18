<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Sidebar from '@/components/Sidebar.vue'

const auth = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <!-- залогинен: сайдбар + контент -->
    <div v-if="auth.isAuthenticated" class="flex">
      <Sidebar />
      <main class="flex-1 p-8 max-w-6xl">
        <RouterView />
      </main>
    </div>

    <!-- не залогинен: центрированные формы -->
    <main v-else class="max-w-5xl mx-auto p-6">
      <RouterView />
    </main>
  </div>
</template>