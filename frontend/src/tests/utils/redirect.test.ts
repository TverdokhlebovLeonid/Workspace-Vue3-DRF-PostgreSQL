import { describe, expect, it } from 'vitest'

import { sanitizeRedirectPath } from '@/utils/redirect'

describe('sanitizeRedirectPath', () => {
  it('returns fallback for missing or invalid values', () => {
    expect(sanitizeRedirectPath(undefined)).toBe('/schedule')
    expect(sanitizeRedirectPath(null)).toBe('/schedule')
    expect(sanitizeRedirectPath('')).toBe('/schedule')
    expect(sanitizeRedirectPath(123)).toBe('/schedule')
  })

  it('allows safe relative paths', () => {
    expect(sanitizeRedirectPath('/schedule')).toBe('/schedule')
    expect(sanitizeRedirectPath('/profile')).toBe('/profile')
    expect(sanitizeRedirectPath('/admin/employees')).toBe('/admin/employees')
  })

  it('blocks open redirects', () => {
    expect(sanitizeRedirectPath('//evil.com')).toBe('/schedule')
    expect(sanitizeRedirectPath('https://evil.com')).toBe('/schedule')
    expect(sanitizeRedirectPath('http://evil.com/path')).toBe('/schedule')
  })

  it('uses custom fallback', () => {
    expect(sanitizeRedirectPath('https://evil.com', '/home')).toBe('/home')
  })
})
