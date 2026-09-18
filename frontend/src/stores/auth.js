import { defineStore } from 'pinia'
import axios from 'axios'

const API = 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.access,
  },

  actions: {
    async login(username, password) {
      const { data } = await axios.post(`${API}/auth/login`, { username, password })
      this.setTokens(data.access_token, data.refresh_token)
      this.user = { username }
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    async register(username, email, password) {
      await axios.post(`${API}/auth/register`, { username, email, password })
      await this.login(username, password)  // сразу логинимся
    },

    async refreshAccess() {
      const { data } = await axios.post(`${API}/auth/refresh`, {
        refresh_token: this.refresh,
      })
      this.setTokens(data.access_token, data.refresh_token)
    },

    setTokens(access, refresh) {
      this.access = access
      this.refresh = refresh
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
    },

    logout() {
      this.access = null
      this.refresh = null
      this.user = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('user')
    },
  },
})