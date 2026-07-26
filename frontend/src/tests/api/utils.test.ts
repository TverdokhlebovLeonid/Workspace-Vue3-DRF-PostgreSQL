import { describe, expect, it } from 'vitest'

import { unwrapList } from '@/api/utils'

describe('unwrapList', () => {
  it('returns plain array as-is', () => {
    const items = [{ id: '1' }, { id: '2' }]
    expect(unwrapList(items)).toBe(items)
    expect(unwrapList(items)).toEqual([{ id: '1' }, { id: '2' }])
  })

  it('returns results from paginated response', () => {
    expect(unwrapList({ results: [{ id: '1' }] })).toEqual([{ id: '1' }])
  })

  it('returns empty array when paginated response has no results', () => {
    expect(unwrapList({})).toEqual([])
    expect(unwrapList({ results: [] })).toEqual([])
  })
})
