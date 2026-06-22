import { API_SCHEDULES_PREFIX } from '@/api/constants'
import Http from '@/api/http'
import { unwrapList, type Paginated } from '@/api/utils'
import type { EntityId } from '@/types/id'
import type {
  Employee,
  EmployeePayload,
  Location,
  LocationPayload,
  ScheduleGrid,
  ScheduleHistoryGrid,
  ScheduleShiftChange,
  WorkRule
} from '@/types/schedules'

const schedulesApi = {
  async getGrid(start?: string) {
    const { data } = await Http.get<ScheduleGrid>(`${API_SCHEDULES_PREFIX}/grid/`, {
      params: start ? { start } : undefined
    })
    return data
  },
  async getGridHistory(before: string, weeks = 2) {
    const { data } = await Http.get<ScheduleHistoryGrid>(`${API_SCHEDULES_PREFIX}/grid/history/`, {
      params: { before, weeks }
    })
    return data
  },
  async generate(start?: string) {
    const { data } = await Http.post<{ created_shifts: number; grid: ScheduleGrid }>(
      `${API_SCHEDULES_PREFIX}/generate/`,
      { start }
    )
    return data
  },
  async saveChanges(changes: ScheduleShiftChange[]) {
    const { data } = await Http.post<{ saved: number; grid: ScheduleGrid }>(
      `${API_SCHEDULES_PREFIX}/grid/save/`,
      { changes }
    )
    return data
  },
  async getLocations() {
    const { data } = await Http.get<Paginated<Location>>(`${API_SCHEDULES_PREFIX}/locations/`)
    return unwrapList(data)
  },
  async createLocation(payload: LocationPayload) {
    const { data } = await Http.post<Location>(`${API_SCHEDULES_PREFIX}/locations/`, payload)
    return data
  },
  async updateLocation(id: EntityId, payload: Partial<LocationPayload>) {
    const { data } = await Http.patch<Location>(`${API_SCHEDULES_PREFIX}/locations/${id}/`, payload)
    return data
  },
  deleteLocation(id: EntityId) {
    return Http.delete(`${API_SCHEDULES_PREFIX}/locations/${id}/`)
  },
  async getWorkRules() {
    const { data } = await Http.get<WorkRule[]>(`${API_SCHEDULES_PREFIX}/work-rules/`)
    return data
  },
  async getEmployees() {
    const { data } = await Http.get<Paginated<Employee>>(`${API_SCHEDULES_PREFIX}/employees/`)
    return unwrapList(data)
  },
  async createEmployee(payload: EmployeePayload) {
    const { data } = await Http.post<Employee>(`${API_SCHEDULES_PREFIX}/employees/`, payload)
    return data
  },
  async updateEmployee(id: EntityId, payload: Partial<EmployeePayload>) {
    const { data } = await Http.patch<Employee>(`${API_SCHEDULES_PREFIX}/employees/${id}/`, payload)
    return data
  },
  deleteEmployee(id: EntityId) {
    return Http.delete(`${API_SCHEDULES_PREFIX}/employees/${id}/`)
  }
}

export default schedulesApi
