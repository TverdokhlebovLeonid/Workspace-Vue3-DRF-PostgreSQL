import { describe, expect, it } from 'vitest'

import type { Employee } from '@/types/schedules'
import { isWeekend, sortEmployeesForPalette } from '@/utils/schedule'

function employee(nickname: string, isActive: boolean): Employee {
  return {
    id: nickname,
    last_name: nickname,
    first_name: '',
    nickname,
    email: '',
    phone: '',
    location_ids: [],
    work_rule_ids: [],
    locations: [],
    work_rules: [],
    cycle_start_date: null,
    is_active: isActive
  }
}

describe('isWeekend', () => {
  it('returns false for weekdays', () => {
    expect(isWeekend(0)).toBe(false)
    expect(isWeekend(1)).toBe(false)
    expect(isWeekend(2)).toBe(false)
    expect(isWeekend(3)).toBe(false)
    expect(isWeekend(4)).toBe(false)
  })

  it('returns true for Saturday and Sunday', () => {
    expect(isWeekend(5)).toBe(true)
    expect(isWeekend(6)).toBe(true)
  })
})

describe('sortEmployeesForPalette', () => {
  it('keeps only active employees', () => {
    const employees = [
      employee('Anna', true),
      employee('Bob', false),
      employee('Chris', true)
    ]

    expect(sortEmployeesForPalette(employees).map((item) => item.nickname)).toEqual([
      'Anna',
      'Chris'
    ])
  })

  it('sorts active employees by nickname', () => {
    const employees = [
      employee('Zara', true),
      employee('Anna', true),
      employee('Mike', true),
      employee('Inactive', false)
    ]

    expect(sortEmployeesForPalette(employees).map((item) => item.nickname)).toEqual([
      'Anna',
      'Mike',
      'Zara'
    ])
  })
})
