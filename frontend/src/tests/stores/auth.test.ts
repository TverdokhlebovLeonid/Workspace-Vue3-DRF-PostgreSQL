import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import authApi from '@/api/auth'
import { USER_ROLE } from '@/api/enum'
import usersApi from '@/api/users'
import { clearToken, getAccessToken, setHeadersToken } from '@/services/authToken'
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
