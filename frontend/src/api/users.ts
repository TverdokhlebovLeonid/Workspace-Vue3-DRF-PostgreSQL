import { API_AUTH_PREFIX } from '@/api/constants'
import Http from '@/api/http'
import type { AppLanguage } from '@/i18n'
import type { User } from '@/types/auth'

const getMe = async () => {
  const { data } = await Http.get<User>(`${API_AUTH_PREFIX}/me/`)
  return data
}
const updateMe = async (payload: { language: AppLanguage }) => {
  const { data } = await Http.patch<User>(`${API_AUTH_PREFIX}/me/`, payload)
  return data
}
const changePassword = async (payload: { current_password: string; new_password: string }) => {
  const { data } = await Http.post<{ detail: string }>(`${API_AUTH_PREFIX}/me/password/`, payload)
  return data
}
export default {
  getMe,
  updateMe,
  changePassword
}
