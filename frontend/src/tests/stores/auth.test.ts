import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import authApi from '@/api/auth'
import { USER_ROLE } from '@/api/enum'
import usersApi from '@/api/users'
import { LANGUAGE_STORAGE_KEY } from '@/i18n'
import { getDataFromStorage } from '@/services/localStorage'
import { getAccessToken, setHeadersToken } from '@/services/authToken'
import { useAuthStore } from '@/stores/auth'
import type { User } from '@/types/auth'

let memoryToken: string | null = null

vi.mock('@/api/auth', () => ({
  default: {
    login: vi.fn(),
    refreshToken: vi.fn(),
    logout: vi.fn()
  }
}))

vi.mock('@/api/users', () => ({
  default: {
    getMe: vi.fn(),
    updateMe: vi.fn(),
    changePassword: vi.fn()
  }
}))

vi.mock('@/services/authToken', () => ({
  getAccessToken: () => memoryToken,
  setHeadersToken: (token: string | null) => {
    memoryToken = token
  },
  clearToken: () => {
    memoryToken = null
  }
}))

const mockUser: User = {
  id: 'user-1',
  username: 'admin',
  email: 'admin@example.com',
  first_name: 'Ada',
  last_name: 'Admin',
  role: USER_ROLE.admin,
  language: 'en'
}

describe('auth store login and initialization', () => {
  beforeEach(() => {
    memoryToken = null
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('logoutLocal clears user and token', async () => {
    setHeadersToken('access-token')
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)
    const store = useAuthStore()
    await store.initialize()

    store.logoutLocal()

    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(getAccessToken()).toBeNull()
  })

  it('syncAccessToken syncs access token ref from memory', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)

    setHeadersToken('memory-token')
    store.syncAccessToken()

    expect(store.isAuthenticated).toBe(true)
  })

  it('initialize without token keeps guest session', async () => {
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('no refresh'))
    const store = useAuthStore()

    await store.initialize()

    expect(store.initialized).toBe(true)
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(usersApi.getMe).not.toHaveBeenCalled()
  })

  it('initialize with token loads current user via getMe', async () => {
    setHeadersToken('access-token')
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)
    const store = useAuthStore()

    await store.initialize()

    expect(usersApi.getMe).toHaveBeenCalledTimes(1)
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
    expect(store.isAdmin).toBe(true)
  })

  it('initialize logs out when getMe fails and restore fails', async () => {
    setHeadersToken('access-token')
    vi.mocked(usersApi.getMe).mockRejectedValue(new Error('unauthorized'))
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('refresh failed'))
    const store = useAuthStore()

    await store.initialize()

    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(getAccessToken()).toBeNull()
  })

  it('login stores access token and loads user', async () => {
    vi.mocked(authApi.login).mockImplementation(async () => {
      setHeadersToken('login-token')
      return { access: 'login-token' }
    })
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)
    const store = useAuthStore()

    await store.login({ username: 'admin', password: 'secret' })

    expect(authApi.login).toHaveBeenCalledWith({ username: 'admin', password: 'secret' })
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
    expect(getAccessToken()).toBe('login-token')
    expect(store.loading).toBe(false)
  })

  it('logout calls API and clears local session', async () => {
    setHeadersToken('access-token')
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)
    vi.mocked(authApi.logout).mockResolvedValue(undefined)
    const store = useAuthStore()
    await store.initialize()

    await store.logout()

    expect(authApi.logout).toHaveBeenCalledTimes(1)
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(getAccessToken()).toBeNull()
  })
})

describe('auth store session restore and language', () => {
  beforeEach(() => {
    memoryToken = null
    localStorage.clear()
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('restores session when refresh succeeds', async () => {
    vi.mocked(authApi.refreshToken).mockImplementation(async () => {
      setHeadersToken('refreshed-token')
      return { access: 'refreshed-token' }
    })
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)
    const store = useAuthStore()

    await store.initialize()

    expect(authApi.refreshToken).toHaveBeenCalled()
    expect(store.user).toEqual(mockUser)
    expect(store.isAuthenticated).toBe(true)
    expect(getAccessToken()).toBe('refreshed-token')
  })

  it('clears local session when refresh fails', async () => {
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('refresh failed'))
    const store = useAuthStore()

    await store.initialize()

    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(getAccessToken()).toBeNull()
    expect(usersApi.getMe).not.toHaveBeenCalled()
  })

  it('clears local session when refresh succeeds but getMe fails', async () => {
    vi.mocked(authApi.refreshToken).mockImplementation(async () => {
      setHeadersToken('refreshed-token')
      return { access: 'refreshed-token' }
    })
    vi.mocked(usersApi.getMe).mockRejectedValue(new Error('getMe failed'))
    const store = useAuthStore()

    await store.initialize()

    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(getAccessToken()).toBeNull()
  })

  it('calls refresh with skipLoginRedirect', async () => {
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('refresh failed'))
    const store = useAuthStore()

    await store.initialize()

    expect(authApi.refreshToken).toHaveBeenCalledWith({ skipLoginRedirect: true })
  })

  it('setLanguage for guest saves language to localStorage', async () => {
    const store = useAuthStore()

    await store.setLanguage('ru')

    expect(store.language).toBe('ru')
    expect(getDataFromStorage(LANGUAGE_STORAGE_KEY)).toBe('ru')
    expect(usersApi.updateMe).not.toHaveBeenCalled()
  })

  it('setLanguage for authenticated user updates profile via API', async () => {
    setHeadersToken('access-token')
    const updatedUser = { ...mockUser, language: 'ru' as const }
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)
    vi.mocked(usersApi.updateMe).mockResolvedValue(updatedUser)
    const store = useAuthStore()
    await store.initialize()

    await store.setLanguage('ru')

    expect(usersApi.updateMe).toHaveBeenCalledWith({ language: 'ru' })
    expect(store.user).toEqual(updatedUser)
    expect(store.language).toBe('ru')
  })
})
