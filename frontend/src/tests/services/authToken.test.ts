import { beforeEach, describe, expect, it } from 'vitest'

import Http from '@/api/http'
import { TOKEN_KEY } from '@/api/enum'
import { clearToken, getAccessToken, setHeadersToken } from '@/services/authToken'
import { getDataFromStorage, saveDataInStorage } from '@/services/localStorage'

describe('authToken service', () => {
  beforeEach(() => {
    clearToken()
  })

  it('sets Authorization header via setHeadersToken', () => {
    setHeadersToken('access-token-123')

    expect(getAccessToken()).toBe('access-token-123')
    expect(Http.defaults.headers.Authorization).toBe('Bearer access-token-123')
  })

  it('clears header and legacy localStorage keys via clearToken', () => {
    saveDataInStorage(TOKEN_KEY.access, 'legacy-access')
    saveDataInStorage(TOKEN_KEY.refresh, 'legacy-refresh')
    setHeadersToken('access-token-123')

    clearToken()

    expect(getAccessToken()).toBeNull()
    expect(Http.defaults.headers.Authorization).toBeUndefined()
    expect(getDataFromStorage(TOKEN_KEY.access)).toBeNull()
    expect(getDataFromStorage(TOKEN_KEY.refresh)).toBeNull()
  })

  it('reads access token from in-memory storage', () => {
    expect(getAccessToken()).toBeNull()

    setHeadersToken('memory-only-token')

    expect(getAccessToken()).toBe('memory-only-token')
  })
})
