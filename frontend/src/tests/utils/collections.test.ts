import { describe, expect, it } from 'vitest'

import { sortByNickname, toggleInArray } from '@/utils/collections'

describe('toggleInArray', () => {
  it('adds value when it is missing', () => {
    expect(toggleInArray(['a', 'b'], 'c')).toEqual(['a', 'b', 'c'])
  })

  it('removes value when it is already present', () => {
    expect(toggleInArray(['a', 'b', 'c'], 'b')).toEqual(['a', 'c'])
  })
})

describe('sortByNickname', () => {
  it('sorts items by nickname using current locale', () => {
    const items = [{ nickname: 'Zara' }, { nickname: 'Anna' }, { nickname: 'Mike' }]

    expect(sortByNickname(items).map((item) => item.nickname)).toEqual(['Anna', 'Mike', 'Zara'])
  })
})
