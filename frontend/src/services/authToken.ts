import { TOKEN_KEY } from '@/api/enum'
import Http from '@/api/http'
import { removeDataFromStorage } from '@/services/localStorage'

let accessTokenMemory: string | null = null

export const getAccessToken = (): string | null => accessTokenMemory

export const setHeadersToken = (token: string | null) => {
  accessTokenMemory = token
  if (token) {
    Http.defaults.headers.Authorization = `Bearer ${token}`
    return
  }
  delete Http.defaults.headers.Authorization
}

export const clearToken = () => {
  setHeadersToken(null)
  removeDataFromStorage(TOKEN_KEY.access)
  removeDataFromStorage(TOKEN_KEY.refresh)
}
