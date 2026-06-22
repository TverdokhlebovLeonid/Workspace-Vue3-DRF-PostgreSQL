import type { EntityId } from '@/types/id'

export type DocumentAccessEntry = {
  employee_id: EntityId
  granted_at: string
  granted_by_username: string | null
}
export type DocumentItem = {
  id: EntityId
  title: string
  file_name: string
  created_at: string
  employee_ids: EntityId[]
  access_entries: DocumentAccessEntry[]
  can_download: boolean
}
export type DocumentAccessPayload = {
  employee_ids: EntityId[]
}
