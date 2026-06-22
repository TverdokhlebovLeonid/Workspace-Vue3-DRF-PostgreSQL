import { TOKEN_KEY, USER_ROLE } from '@/api/enum'
import authApi from '@/api/auth'
import usersApi from '@/api/users'
import {
  applyLocale,
  i18n,
  readGuestLanguage,
  resolveUserLanguage,
  saveGuestLanguage,
  type AppLanguage
} from '@/i18n'
import { clearToken } from '@/services/authToken'
import { getDataFromStorage } from '@/services/localStorage'
import { useNotificationStore } from '@/stores/notification'
import type { LoginCredentials, User } from '@/types/auth'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
function readAccessToken(): string | null {
  return getDataFromStorage<string>(TOKEN_KEY.access)
}
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const accessToken = ref<string | null>(readAccessToken())
  const language = ref<AppLanguage>(readGuestLanguage())
  const isAuthenticated = computed(() => Boolean(accessToken.value))
  const username = computed(() => user.value?.username ?? '')
  const role = computed(() => user.value?.role ?? null)
  const isAdmin = computed(() => user.value?.role === USER_ROLE.admin)
  const displayName = computed(() => {
    const current = user.value
    if (!current) return ''
    const fullName = [current.last_name, current.first_name].filter(Boolean).join(' ')
    return fullName || current.username
  })
  function syncAccessToken() {
    accessToken.value = readAccessToken()
  }
  function applyLanguage(next: AppLanguage) {
    language.value = next
    applyLocale(next)
  }
  async function setLanguage(next: AppLanguage) {
    applyLanguage(next)
    if (!isAuthenticated.value) {
      saveGuestLanguage(next)
      return
    }
    try {
      user.value = await usersApi.updateMe({ language: next })
      useNotificationStore().add({
        text: i18n.global.t('common.updateSuccess'),
        type: 'success'
      })
    } catch {
      applyLanguage(resolveUserLanguage(user.value?.language))
    }
  }
  async function initialize() {
    if (initialized.value) return
    initialized.value = true
    syncAccessToken()
    if (!accessToken.value) {
      user.value = null
      applyLanguage(readGuestLanguage())
      return
    }
    try {
      user.value = await usersApi.getMe()
      applyLanguage(resolveUserLanguage(user.value.language))
    } catch {
      logout()
    }
  }
  async function login(credentials: LoginCredentials) {
    loading.value = true
    try {
      await authApi.login(credentials)
      syncAccessToken()
      user.value = await usersApi.getMe()
      applyLanguage(resolveUserLanguage(user.value.language))
    } finally {
      loading.value = false
    }
  }
  function logout() {
    clearToken()
    accessToken.value = null
    user.value = null
    applyLanguage(readGuestLanguage())
  }
  return {
    user,
    initialized,
    loading,
    language,
    isAuthenticated,
    username,
    role,
    isAdmin,
    displayName,
    initialize,
    login,
    logout,
    setLanguage,
    syncAccessToken
  }
})
