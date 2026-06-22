import type { Employee } from '@/types/schedules'
import { sortByNickname } from '@/utils/collections'

export function isWeekend(weekday: number): boolean {
  return weekday >= 5
}

export function sortEmployeesForPalette(employees: Employee[]): Employee[] {
  return sortByNickname(employees.filter((employee) => employee.is_active))
}
