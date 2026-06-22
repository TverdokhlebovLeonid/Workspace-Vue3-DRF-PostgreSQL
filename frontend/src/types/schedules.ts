import type { EntityId } from '@/types/id'

export type LocationType = 'STORE' | 'CASH_REGISTER'
export type Location = {
  id: EntityId
  location_type: LocationType
  location_type_label: string
  name: string
  is_active: boolean
  sort_order: number
}
export type WorkRule = {
  id: EntityId
  code: string
  name: string
  kind: string
  kind_label: string
  description: string
}
export type Employee = {
  id: EntityId
  last_name: string
  first_name: string
  nickname: string
  email: string
  phone: string
  location_ids: EntityId[]
  work_rule_ids: EntityId[]
  locations: Location[]
  work_rules: WorkRule[]
  cycle_start_date: string | null
  is_active: boolean
  has_user?: boolean
}
export type ScheduleGridCell = {
  date: string
  employee_id: EntityId | null
  nickname: string
}
export type ScheduleGridRow = {
  location: {
    id: EntityId
    name: string
    location_type: LocationType
    location_type_label: string
  }
  cells: ScheduleGridCell[]
}
export type ScheduleGridDay = {
  date: string
  weekday: number
  weekday_label: string
  display: string
}
export type ScheduleGridWeek = {
  week_index: number
  week_start: string
  is_past?: boolean
  days: ScheduleGridDay[]
  rows: ScheduleGridRow[]
}
export type ScheduleGrid = {
  year: number
  current_start_date: string
  current_end_date: string
  start_date: string
  end_date: string
  weeks_count: number
  days_count: number
  weeks: ScheduleGridWeek[]
}
export type ScheduleHistoryGrid = {
  before_date: string
  start_date: string
  end_date: string
  weeks_count: number
  weeks: ScheduleGridWeek[]
}
export type LocationPayload = {
  location_type: LocationType
  name: string
  is_active?: boolean
  sort_order?: number
}
export type EmployeePayload = {
  last_name: string
  first_name: string
  nickname: string
  email?: string
  phone?: string
  location_ids: EntityId[]
  work_rule_ids: EntityId[]
  cycle_start_date?: string
  is_active?: boolean
  password?: string
}
export type ScheduleShiftChange = {
  date: string
  location_id: EntityId
  employee_id: EntityId | null
}
