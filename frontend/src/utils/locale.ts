import { i18n } from '@/i18n'

export function currentLocale(): 'ru' | 'en' {
  return i18n.global.locale.value === 'ru' ? 'ru' : 'en'
}
