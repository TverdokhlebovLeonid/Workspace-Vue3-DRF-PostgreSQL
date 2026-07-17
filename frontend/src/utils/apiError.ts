import { isAxiosError } from 'axios'

export type ScheduleSaveErrorBody = {
  detail?: string | string[]
  code?: string
  date?: string
  location_id?: string
  location_name?: string
  employee_nickname?: string
  employee_id?: string
}

export function getApiErrorBody(error: unknown): ScheduleSaveErrorBody | undefined {
  if (!isAxiosError(error)) return undefined
  const data: unknown = error.response?.data
  if (typeof data === 'string') {
    return { detail: data }
  }
  if (Array.isArray(data) && typeof data[0] === 'string') {
    return { detail: data[0] }
  }
  if (data && typeof data === 'object') {
    return data as ScheduleSaveErrorBody
  }
  return undefined
}

export function getApiErrorDetail(error: unknown): string | undefined {
  const body = getApiErrorBody(error)
  if (!body?.detail) return undefined
  if (typeof body.detail === 'string') return body.detail
  if (Array.isArray(body.detail) && body.detail.length > 0) {
    return String(body.detail[0])
  }
  return undefined
}
