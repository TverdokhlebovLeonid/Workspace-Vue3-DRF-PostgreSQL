import type { EntityId } from '@/types/id'
import type { USER_ROLE } from '@/api/enum'

export type UserRole = `${USER_ROLE}`
export type LoginCredentials = {
  username: string
  password: string
}
export type AuthTokens = {
  access: string
  refresh: string
}
export type User = {
  id: EntityId
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  language: 'en' | 'ru'
}
