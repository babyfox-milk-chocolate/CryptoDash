<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/api/axios'
import PriceChart from '@/components/PriceChart.vue'

const coins = ref([])
const loading = ref(false)
const error = ref('')
const newCoin = ref('')
const adding = ref(false)
const warning = ref('')

let intervalId = null

async function fetchDashboard() {
  try {
    const { data } = await api.get('/watchlist/dashboard')
    coins.value = data
  } catch (e) {
    const status = e.response?.status
    if (status === 429){
      error.value = 'Мы получили ограничение запросов. Данные обновятся через 1 минуту'
    }else if (status === 401){
      // эту ошибку обработает интерцептор 
      return 
    }else {
      error.value = 'Не удалось загрузить данные'
    }
  }
}

async function addCoin() {
  const id = newCoin.value.trim().toLowerCase()
  if (!id) return
  adding.value = true
  error.value = ''
  try {
    await api.post('/watchlist', { coin_id: id })
    newCoin.value = ''
    await fetchDashboard()  // перезагружаем с новой монетой
  } catch (e) {
    error.value = e.response?.data?.detail || 'Не удалось добавить монету'
  } finally {
    adding.value = false
  }
}

async function removeCoin(coinId) {
  try {
    await api.delete(`/watchlist/${coinId}`)
    coins.value = coins.value.filter((c) => c.id !== coinId)
  } catch (e) {
    error.value = 'Не удалось удалить монету'
  }
}

// сводная статистика
const totalMarketCap = computed(() =>
  coins.value.reduce((sum, c) => sum + (c.market_cap || 0), 0)
)
const avgChange = computed(() => {
  if (coins.value.length === 0) return 0
  const sum = coins.value.reduce((s, c) => s + (c.price_change_percentage_24h || 0), 0)
  return sum / coins.value.length
})

function formatPrice(p) {
  if (p == null) return '—'
  return p < 1 ? `$${p.toFixed(4)}` : `$${p.toLocaleString('en-US', { maximumFractionDigits: 2 })}`
}
function formatCap(c) {
  if (!c) return '—'
  if (c >= 1e9) return `$${(c / 1e9).toFixed(2)}B`
  if (c >= 1e6) return `$${(c / 1e6).toFixed(2)}M`
  return `$${c.toLocaleString()}`
}

onMounted(async () => {
  loading.value = true
  await fetchDashboard()
  loading.value = false
  // автообновление каждые 60с (совпадает с TTL кэша)
  intervalId = setInterval(fetchDashboard, 60000)
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)  // чистим таймер при уходе со страницы
})

const selectedCoin = ref(null)   // монета для модалки
const coinDetail = ref(null)     // {market, history}
const detailLoading = ref(false)

async function openCoin(coin) {
  selectedCoin.value = coin
  detailLoading.value = true
  coinDetail.value = null
  try {
    const { data } = await api.get(`/coins/${coin.id}?days=30`)
    coinDetail.value = data
  } catch (e) {
    const status = e.response?.status
    if (status === 429){
      warning.value = '...'
      error.value = 'Мы получили ограничение запросов. Данные обновятся через 1 минут'
    }else if (status === 401){
      return 
    }else{
      error.value = 'Ограничение кол-ва запросов. Ждем минуту... '
    }
  } finally {
    detailLoading.value = false
  }
}

function closeCoin() {
  selectedCoin.value = null
  coinDetail.value = null
}
</script>

<template>
  <div>
    <!-- сводные карточки -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
      <div class="bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 rounded-2xl p-5">
        <div class="text-gray-400 text-sm">Монет в списке</div>
        <div class="text-3xl font-bold mt-1">{{ coins.length }}</div>
      </div>
      <div class="bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 rounded-2xl p-5">
        <div class="text-gray-400 text-sm">Суммарная капитализация</div>
        <div class="text-3xl font-bold mt-1">{{ formatCap(totalMarketCap) }}</div>
      </div>
      <div class="bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 rounded-2xl p-5">
        <div class="text-gray-400 text-sm">Средний рост 24ч</div>
        <div class="text-3xl font-bold mt-1" :class="avgChange >= 0 ? 'text-emerald-400' : 'text-red-400'">
          {{ avgChange >= 0 ? '+' : '' }}{{ avgChange.toFixed(2) }}%
        </div>
      </div>
    </div>

    <!-- добавление монеты -->
    <div class="flex gap-2 mb-6">
      <input v-model="newCoin" placeholder="ID монеты (напр. bitcoin, solana)" @keyup.enter="addCoin"
        class="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-violet-500" />
      <button @click="addCoin" :disabled="adding"
        class="bg-violet-600 hover:bg-violet-700 px-6 rounded-xl font-medium disabled:opacity-50">
        {{ adding ? '...' : 'Добавить' }}
      </button>
    </div>

    <div v-if="error" class="mb-4 text-sm text-red-400 bg-red-900/30 p-3 rounded-xl">{{ error }}</div>
    <div v-if="loading" class="text-gray-500 text-center py-12">Загрузка...</div>

    <div v-else-if="coins.length === 0" class="text-gray-500 text-center py-16">
      Watchlist пуст. Добавьте первую монету!
    </div>

    <!-- сетка карточек монет -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="coin in coins" :key="coin.id" @click="openCoin(coin)"
        class="group bg-gray-800/60 border border-gray-700 rounded-2xl p-5 hover:border-violet-500/50 transition">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <img v-if="coin.image" :src="coin.image" :alt="coin.name" class="w-9 h-9 rounded-full" />
            <div>
              <div class="font-semibold">{{ coin.name }}</div>
              <div class="text-xs text-gray-500 uppercase">{{ coin.symbol }}</div>
            </div>
          </div>
          <button @click.stop="removeCoin(coin.id)"
            class="text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition">✕</button>
        </div>
        <div class="text-2xl font-bold">{{ formatPrice(coin.current_price) }}</div>
        <div class="flex items-center justify-between mt-2">
          <span class="text-sm px-2 py-0.5 rounded-lg"
            :class="(coin.price_change_percentage_24h || 0) >= 0
              ? 'text-emerald-400 bg-emerald-400/10'
              : 'text-red-400 bg-red-400/10'">
            {{ (coin.price_change_percentage_24h || 0) >= 0 ? '▲' : '▼' }}
            {{ Math.abs(coin.price_change_percentage_24h || 0).toFixed(2) }}%
          </span>
          <span class="text-xs text-gray-500">{{ formatCap(coin.market_cap) }}</span>
        </div>
      </div>
    </div>

    <div v-if="selectedCoin" @click="closeCoin"
      class="fixed inset-0 bg-black/60 flex items-center justify-center p-4 z-50">
      <div @click.stop class="bg-gray-800 border border-gray-700 rounded-2xl p-6 w-full max-w-2xl">
        <div class="flex items-center justify-between mb-6">
          <div class="flex items-center gap-3">
            <img v-if="selectedCoin.image" :src="selectedCoin.image" class="w-10 h-10 rounded-full" />
            <div>
              <div class="text-lg font-bold">{{ selectedCoin.name }}</div>
              <div class="text-sm text-gray-500">{{ formatPrice(selectedCoin.current_price) }}</div>
            </div>
          </div>
          <button @click="closeCoin" class="text-gray-500 hover:text-gray-300 text-xl">✕</button>
        </div>

        <div v-if="detailLoading" class="h-64 flex items-center justify-center text-gray-500">Загрузка графика...</div>
        <PriceChart v-else-if="coinDetail?.history?.prices"
          :prices="coinDetail.history.prices"
          :up="(selectedCoin.price_change_percentage_24h || 0) >= 0" />
        <div class="text-xs text-gray-500 text-center mt-4">История цены за 30 дней</div>
      </div>
    </div>

  </div>
</template>