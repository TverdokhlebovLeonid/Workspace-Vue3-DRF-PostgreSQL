import { API_AUTH_PREFIX } from '@/api/constants'
import Http from '@/api/http'
import { clearToken, setHeadersToken } from '@/services/authToken'
import type { LoginCredentials } from '@/types/auth'

type AccessTokenResponse = {
  access: string
}

type RefreshOptions = {
  skipLoginRedirect?: boolean
}

const setAccessToken = (token: string) => {
  setHeadersToken(token)
}

const login = async (credentials: LoginCredentials) => {
  clearToken()
  const { username, password } = credentials
  const { data } = await Http.post<AccessTokenResponse>(`${API_AUTH_PREFIX}/jwt/create/`, {
    username,
    password
  })
  if (data.access) setAccessToken(data.access)
  return data
}

const refreshToken = async (options: RefreshOptions = {}) => {
  const { data } = await Http.post<AccessTokenResponse>(
    `${API_AUTH_PREFIX}/jwt/refresh/`,
    {},
    {
      isRefreshToken: true,
      skipGlobalError: true,
      skipLoginRedirect: options.skipLoginRedirect
    }
  )
  if (data.access) setAccessToken(data.access)
  return data
}

const logout = async () => {
  try {
    await Http.post(`${API_AUTH_PREFIX}/logout/`, {}, { skipGlobalError: true })
  } catch {
    // Cookie/session may already be invalid; still clear local state.
  } finally {
    clearToken()
  }
}

export default {
  login,
  refreshToken,
  logout
}
