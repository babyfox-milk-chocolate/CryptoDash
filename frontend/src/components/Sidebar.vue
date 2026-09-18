<script setup>
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { LayoutDashboard, Briefcase, Sprout, Star, TrendingUp, Settings } from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}

const menu = [
  { name: 'Dashboard', icon: LayoutDashboard, to: '/', active: true },
  { name: 'Portfolio', icon: Briefcase, active: false },
  { name: 'Farms', icon: Sprout, active: false },
  { name: 'Watchlist', icon: Star, active: false },
  { name: 'Analytics', icon: TrendingUp, active: false },
  { name: 'Settings', icon: Settings, active: false },
]
</script>

<template>
  <aside class="w-60 bg-gray-800/80 border-r border-gray-700 flex flex-col shrink-0 h-screen sticky top-0">
    <!-- логотип -->
    <div class="px-6 py-6 flex items-center gap-2">
      <span class="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
        CryptoDash.IO
      </span>
    </div>

    <!-- меню -->
    <nav class="flex-1 px-3 space-y-1">
      <template v-for="item in menu" :key="item.name">
        <!-- рабочий пункт -->
        <RouterLink v-if="item.active" :to="item.to"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition"
          active-class="bg-violet-600/20 text-violet-300"
          :class="{ 'text-gray-400 hover:bg-gray-700/50': true }">
          <span><component :is="item.icon" :size="20" /></span>
          <span class="text-sm font-medium">{{ item.name }}</span>
        </RouterLink>

        <!-- заглушка (задизейблена) -->
        <div v-else
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-600 cursor-not-allowed relative group">
          <span class="opacity-50"><span><component :is="item.icon" :size="20" /></span></span>
          <span class="text-sm font-medium">{{ item.name }}</span>
        </div>
      </template>
    </nav>

    <!-- юзер + выход внизу -->
    <div class="px-3 py-4 border-t border-gray-700">
      <div class="flex items-center justify-between px-3">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center text-sm font-bold">
            {{ auth.user?.username?.charAt(0).toUpperCase() }}
          </div>
          <span class="text-sm text-gray-300">{{ auth.user?.username }}</span>
        </div>
        <button @click="logout" class="text-gray-500 hover:text-red-400 text-sm" title="Выйти">⏻</button>
      </div>
    </div>
  </aside>
</template>