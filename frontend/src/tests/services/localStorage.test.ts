import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  getDataFromStorage,
  removeDataFromStorage,
  saveDataInStorage
} from '@/services/localStorage'

describe('localStorage service', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('round-trips saved data', () => {
    saveDataInStorage('prefs', { language: 'ru', count: 2 })

    expect(getDataFromStorage<{ language: string; count: number }>('prefs')).toEqual({
      language: 'ru',
      count: 2
    })
  })

  it('returns null for missing key', () => {
    expect(getDataFromStorage('missing')).toBeNull()
  })

  it('removes stored value by key', () => {
    saveDataInStorage('session', { id: '1' })
    removeDataFromStorage('session')

    expect(localStorage.getItem('session')).toBeNull()
    expect(getDataFromStorage('session')).toBeNull()
  })

  it('returns null for invalid JSON', () => {
    localStorage.setItem('broken', '{not-json')
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

    expect(getDataFromStorage('broken')).toBeNull()
    expect(warnSpy).toHaveBeenCalled()
  })
})
