import authApi from '@/api/auth'
import { API_BASE_URL } from '@/api/constants'
import { TOKEN_KEY } from '@/api/enum'
import { i18n } from '@/i18n'
import { getDataFromStorage } from '@/services/localStorage'
import { setHeadersToken } from '@/services/authToken'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import axios, { isAxiosError, type CreateAxiosDefaults } from 'axios'
import router from '@/router'

type AxiosDefaultHeaders = CreateAxiosDefaults['headers']
const token = getDataFromStorage<string>(TOKEN_KEY.access)
const headerToken: AxiosDefaultHeaders = token ? { Authorization: `Bearer ${token}` } : {}
declare module 'axios' {
  export interface AxiosRequestConfig {
    isRefreshToken?: boolean
    _retry?: boolean
    skipGlobalError?: boolean
  }
}
const Http = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    ...headerToken
  } as AxiosDefaultHeaders
})
const setNotification = (msg: string | undefined) => {
  const appStore = useNotificationStore()
  const message = msg || i18n.global.t('common.genericError')
  appStore.add({
    text: message,
    type: 'error'
  })
}
async function redirectToLogin() {
  useAuthStore().logout()
  await router.replace({ name: 'login' })
}
let refreshPromise: Promise<string> | null = null
function refreshAccessToken(refresh: string): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = authApi
      .refreshToken(refresh)
      .then((data) => data.access)
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}
Http.interceptors.response.use(
  (response) => Promise.resolve(response),
  async (error) => {
    if (!isAxiosError(error)) {
      return Promise.reject(error)
    }
    const originalRequest = error.config
    if (!originalRequest) {
      return Promise.reject(error)
    }
    const response = error.response
    if (originalRequest.isRefreshToken) {
      await redirectToLogin()
      return Promise.reject(error)
    }
    if (response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = getDataFromStorage<string>(TOKEN_KEY.refresh)
      if (!refreshToken) {
        await redirectToLogin()
        return Promise.reject(error)
      }
      try {
        const tokenNew = await refreshAccessToken(refreshToken)
        setHeadersToken(tokenNew)
        useAuthStore().syncAccessToken()
        originalRequest.headers = originalRequest.headers ?? {}
        originalRequest.headers.Authorization = `Bearer ${tokenNew}`
        return Http.request(originalRequest)
      } catch {
        await redirectToLogin()
        return Promise.reject(error)
      }
    }
    if (!originalRequest.skipGlobalError) {
      setNotification(getErrorMessage(error))
    }
    return Promise.reject(error)
  }
)
function getErrorMessage(error: unknown): string | undefined {
  if (!isAxiosError(error)) return undefined
  const data = error.response?.data as { error?: string; detail?: string } | undefined
  return data?.error || data?.detail
}
export default Http
