import { describe, expect, it } from 'vitest'

import { makeCellKey, parseCellKey } from '@/utils/scheduleCellKey'

describe('makeCellKey', () => {
  it('joins date and locationId with pipe separator', () => {
    expect(makeCellKey('2026-07-17', 'loc-1')).toBe('2026-07-17|loc-1')
  })
})

describe('parseCellKey', () => {
  it('round-trips keys produced by makeCellKey', () => {
    const key = makeCellKey('2026-07-17', 'loc-1')
    expect(parseCellKey(key)).toEqual({
      date: '2026-07-17',
      locationId: 'loc-1'
    })
  })

  it('returns empty strings for missing parts', () => {
    expect(parseCellKey('|')).toEqual({ date: '', locationId: '' })
    expect(parseCellKey('2026-07-17|')).toEqual({ date: '2026-07-17', locationId: '' })
    expect(parseCellKey('|loc-1')).toEqual({ date: '', locationId: 'loc-1' })
  })

  it('preserves UUID locationId', () => {
    const locationId = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    const key = makeCellKey('2026-07-17', locationId)
    expect(parseCellKey(key)).toEqual({
      date: '2026-07-17',
      locationId
    })
  })
})
