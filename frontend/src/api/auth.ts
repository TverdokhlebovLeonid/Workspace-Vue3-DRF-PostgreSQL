import { API_AUTH_PREFIX } from '@/api/constants'
import { TOKEN_KEY } from '@/api/enum'
import Http from '@/api/http'
import { clearToken, setHeadersToken } from '@/services/authToken'
import { saveDataInStorage } from '@/services/localStorage'
import type { AuthTokens, LoginCredentials } from '@/types/auth'

const setAccessToken = (token: string) => {
  setHeadersToken(token)
  saveDataInStorage(TOKEN_KEY.access, token)
}
const login = async (credentials: LoginCredentials) => {
  clearToken()
  const { username, password } = credentials
  const { data } = await Http.post<AuthTokens>(`${API_AUTH_PREFIX}/jwt/create/`, {
    username,
    password
  })
  if (data.access) setAccessToken(data.access)
  if (data.refresh) saveDataInStorage(TOKEN_KEY.refresh, data.refresh)
  return data
}
const refreshToken = async (refresh: string) => {
  const { data } = await Http.post<AuthTokens>(
    `${API_AUTH_PREFIX}/jwt/refresh/`,
    { refresh },
    { isRefreshToken: true }
  )
  if (data.access) setAccessToken(data.access)
  if (data.refresh) saveDataInStorage(TOKEN_KEY.refresh, data.refresh)
  return data
}
export default {
  login,
  refreshToken
}
