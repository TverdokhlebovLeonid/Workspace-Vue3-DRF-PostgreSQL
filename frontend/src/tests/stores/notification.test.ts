import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useNotificationStore } from '@/stores/notification'

describe('notification store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('adds a notification item', () => {
    const store = useNotificationStore()

    store.add({ text: 'Saved', type: 'success' })

    expect(store.items).toHaveLength(1)
    expect(store.items[0]).toMatchObject({
      text: 'Saved',
      type: 'success'
    })
  })

  it('removes a notification by id', () => {
    const store = useNotificationStore()
    const id = store.add({ text: 'Saved', type: 'success' })
    store.add({ text: 'Failed', type: 'error' })

    store.remove(id)

    expect(store.items).toHaveLength(1)
    expect(store.items[0]?.text).toBe('Failed')
  })

  it('uses default duration of 5000', () => {
    const store = useNotificationStore()

    store.add({ text: 'Info', type: 'info' })

    expect(store.items[0]?.duration).toBe(5000)
  })

  it('keeps custom duration when provided', () => {
    const store = useNotificationStore()

    store.add({ text: 'Quick', type: 'warning', duration: 1500 })

    expect(store.items[0]?.duration).toBe(1500)
  })

  it('keeps at most 8 items and drops the oldest', () => {
    const store = useNotificationStore()

    for (let index = 1; index <= 9; index += 1) {
      store.add({ text: `Message ${index}`, type: 'info' })
    }

    expect(store.items).toHaveLength(8)
    expect(store.items[0]?.text).toBe('Message 2')
    expect(store.items[7]?.text).toBe('Message 9')
  })

  it('increments notification ids', () => {
    const store = useNotificationStore()

    const firstId = store.add({ text: 'First', type: 'info' })
    const secondId = store.add({ text: 'Second', type: 'info' })

    expect(secondId).toBe(firstId + 1)
    expect(store.items.map((item) => item.id)).toEqual([firstId, secondId])
  })
})
