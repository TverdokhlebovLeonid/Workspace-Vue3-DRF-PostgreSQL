import { describe, expect, it } from 'vitest'

import { useScheduleEditor } from '@/composables/useScheduleEditor'
import {
  createScheduleGridFixture,
  editableCellKey,
  pastCellKey
} from '@/tests/fixtures/scheduleGrid'

describe('useScheduleEditor', () => {
  it('loadFromGrid fills weeks from grid data', () => {
    const editor = useScheduleEditor()
    const grid = createScheduleGridFixture()

    editor.loadFromGrid(grid)

    expect(editor.weeks.value).toHaveLength(1)
    expect(editor.weeks.value[0]?.rows[0]?.cells).toHaveLength(3)
  })

  it('marks cells as not dirty immediately after load', () => {
    const editor = useScheduleEditor()
    editor.loadFromGrid(createScheduleGridFixture())

    expect(editor.hasChanges.value).toBe(false)
    expect(editor.isDirty(editableCellKey)).toBe(false)
    expect(editor.dirtyKeys.value).toEqual([])
  })

  it('marks cell as dirty after palette drop', () => {
    const editor = useScheduleEditor()
    editor.loadFromGrid(createScheduleGridFixture())

    editor.handleDrop(editableCellKey, {
      type: 'palette',
      employee_id: 'emp-3',
      nickname: 'Chris'
    })

    expect(editor.isDirty(editableCellKey)).toBe(true)
    expect(editor.hasChanges.value).toBe(true)
  })

  it('tracks dirty keys for changed cells', () => {
    const editor = useScheduleEditor()
    editor.loadFromGrid(createScheduleGridFixture())

    editor.handleDrop(editableCellKey, {
      type: 'palette',
      employee_id: 'emp-3',
      nickname: 'Chris'
    })

    expect(editor.dirtyKeys.value).toEqual([editableCellKey])
  })

  it('treats past cells as read-only for dirty state and drops', () => {
    const editor = useScheduleEditor()
    editor.loadFromGrid(createScheduleGridFixture())

    editor.handleDrop(pastCellKey, {
      type: 'palette',
      employee_id: 'emp-99',
      nickname: 'Past'
    })

    expect(editor.getCell(pastCellKey)?.employee_id).toBe('emp-1')

    const pastCell = editor.getCell(pastCellKey)
    if (pastCell) {
      pastCell.employee_id = 'emp-99'
      pastCell.nickname = 'Past'
    }

    expect(editor.isDirty(pastCellKey)).toBe(false)
    expect(editor.dirtyKeys.value).not.toContain(pastCellKey)
  })

  it('resetChanges restores original grid values', () => {
    const editor = useScheduleEditor()
    editor.loadFromGrid(createScheduleGridFixture())

    editor.handleDrop(editableCellKey, {
      type: 'palette',
      employee_id: 'emp-3',
      nickname: 'Chris'
    })
    editor.resetChanges()

    expect(editor.getCell(editableCellKey)).toEqual({
      date: '2026-07-15',
      employee_id: null,
      nickname: ''
    })
    expect(editor.hasChanges.value).toBe(false)
  })

  it('buildSavePayload returns schedule shift changes', () => {
    const editor = useScheduleEditor()
    editor.loadFromGrid(createScheduleGridFixture())

    editor.handleDrop(editableCellKey, {
      type: 'palette',
      employee_id: 'emp-3',
      nickname: 'Chris'
    })

    expect(editor.buildSavePayload()).toEqual([
      {
        date: '2026-07-15',
        location_id: 'loc-a',
        employee_id: 'emp-3'
      }
    ])
  })
})
