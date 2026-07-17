import type { Employee } from '@/types/schedules'
import { makeCellKey, parseCellKey, type CellKey } from '@/utils/scheduleCellKey'
import type { ScheduleSaveErrorBody } from '@/utils/apiError'

type ResolveErrorKeysOptions = {
  body: ScheduleSaveErrorBody
  dirtyKeys: CellKey[]
  getCell: (key: CellKey) => { employee_id: string | null } | undefined
  employees: Employee[]
}

export function resolveScheduleSaveErrorKeys({
  body,
  dirtyKeys,
  getCell,
  employees
}: ResolveErrorKeysOptions): CellKey[] {
  if (body.code !== 'employee_not_assigned_to_location') {
    if (body.date && body.location_id) {
      return [makeCellKey(body.date, body.location_id)]
    }
    return []
  }
  const keys = new Set<CellKey>()
  if (body.date && body.location_id) {
    keys.add(makeCellKey(body.date, body.location_id))
  }
  const employee = employees.find(
    (item) =>
      (body.employee_id && item.id === body.employee_id) ||
      (body.employee_nickname && item.nickname === body.employee_nickname)
  )
  if (!employee) {
    return [...keys]
  }
  const allowedLocationIds = new Set(employee.locations.map((location) => location.id))
  for (const key of dirtyKeys) {
    const cell = getCell(key)
    const { locationId } = parseCellKey(key)
    if (cell?.employee_id === employee.id && !allowedLocationIds.has(locationId)) {
      keys.add(key)
    }
  }
  return [...keys]
}
