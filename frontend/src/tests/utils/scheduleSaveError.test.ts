import { describe, expect, it } from 'vitest'

import type { Employee, Location } from '@/types/schedules'
import { makeCellKey } from '@/utils/scheduleCellKey'
import { resolveScheduleSaveErrorKeys } from '@/utils/scheduleSaveError'

function location(id: string, name = id): Location {
  return {
    id,
    name,
    location_type: 'STORE',
    location_type_label: 'Store',
    is_active: true,
    sort_order: 0
  }
}

function employee(
  id: string,
  nickname: string,
  assignedLocations: Location[]
): Employee {
  return {
    id,
    last_name: nickname,
    first_name: '',
    nickname,
    email: '',
    phone: '',
    location_ids: assignedLocations.map((item) => item.id),
    work_rule_ids: [],
    locations: assignedLocations,
    work_rules: [],
    cycle_start_date: null,
    is_active: true
  }
}

describe('resolveScheduleSaveErrorKeys', () => {
  const locA = location('loc-a', 'Point A')
  const locB = location('loc-b', 'Point B')
  const maria = employee('emp-maria', 'Maria', [locA])

  it('returns cell key from date and location for unknown error codes', () => {
    const keys = resolveScheduleSaveErrorKeys({
      body: { code: 'validation_error', date: '2026-07-17', location_id: 'loc-b' },
      dirtyKeys: [],
      getCell: () => undefined,
      employees: []
    })

    expect(keys).toEqual([makeCellKey('2026-07-17', 'loc-b')])
  })

  it('includes body cell key for employee_not_assigned_to_location', () => {
    const keys = resolveScheduleSaveErrorKeys({
      body: {
        code: 'employee_not_assigned_to_location',
        date: '2026-07-17',
        location_id: 'loc-b',
        employee_nickname: 'Maria'
      },
      dirtyKeys: [],
      getCell: () => undefined,
      employees: [maria]
    })

    expect(keys).toEqual([makeCellKey('2026-07-17', 'loc-b')])
  })

  it('highlights dirty cells where employee is assigned to unallowed locations', () => {
    const dirtyKeys = [
      makeCellKey('2026-07-17', 'loc-b'),
      makeCellKey('2026-07-18', 'loc-b'),
      makeCellKey('2026-07-19', 'loc-a')
    ]
    const keys = resolveScheduleSaveErrorKeys({
      body: {
        code: 'employee_not_assigned_to_location',
        date: '2026-07-17',
        location_id: 'loc-b',
        employee_nickname: 'Maria'
      },
      dirtyKeys,
      getCell: (key) => ({ employee_id: maria.id }),
      employees: [maria]
    })

    expect(keys).toEqual([
      makeCellKey('2026-07-17', 'loc-b'),
      makeCellKey('2026-07-18', 'loc-b')
    ])
  })

  it('returns only body key when employee is not found', () => {
    const keys = resolveScheduleSaveErrorKeys({
      body: {
        code: 'employee_not_assigned_to_location',
        date: '2026-07-17',
        location_id: 'loc-b',
        employee_nickname: 'Unknown'
      },
      dirtyKeys: [makeCellKey('2026-07-18', 'loc-b')],
      getCell: () => ({ employee_id: 'emp-maria' }),
      employees: [maria]
    })

    expect(keys).toEqual([makeCellKey('2026-07-17', 'loc-b')])
  })

  it('matches employee by employee_id', () => {
    const keys = resolveScheduleSaveErrorKeys({
      body: {
        code: 'employee_not_assigned_to_location',
        date: '2026-07-17',
        location_id: 'loc-b',
        employee_id: 'emp-maria'
      },
      dirtyKeys: [makeCellKey('2026-07-18', 'loc-b')],
      getCell: () => ({ employee_id: maria.id }),
      employees: [maria]
    })

    expect(keys).toEqual([
      makeCellKey('2026-07-17', 'loc-b'),
      makeCellKey('2026-07-18', 'loc-b')
    ])
  })

  it('matches employee by employee_nickname', () => {
    const keys = resolveScheduleSaveErrorKeys({
      body: {
        code: 'employee_not_assigned_to_location',
        date: '2026-07-17',
        location_id: 'loc-b',
        employee_nickname: 'Maria'
      },
      dirtyKeys: [makeCellKey('2026-07-18', 'loc-b')],
      getCell: () => ({ employee_id: maria.id }),
      employees: [maria]
    })

    expect(keys).toEqual([
      makeCellKey('2026-07-17', 'loc-b'),
      makeCellKey('2026-07-18', 'loc-b')
    ])
  })

  it('returns empty list when date and location are missing', () => {
    expect(
      resolveScheduleSaveErrorKeys({
        body: { code: 'validation_error' },
        dirtyKeys: [makeCellKey('2026-07-17', 'loc-b')],
        getCell: () => ({ employee_id: maria.id }),
        employees: [maria]
      })
    ).toEqual([])

    expect(
      resolveScheduleSaveErrorKeys({
        body: {
          code: 'employee_not_assigned_to_location',
          employee_nickname: 'Unknown'
        },
        dirtyKeys: [makeCellKey('2026-07-17', 'loc-b')],
        getCell: () => ({ employee_id: maria.id }),
        employees: [maria]
      })
    ).toEqual([])
  })
})
