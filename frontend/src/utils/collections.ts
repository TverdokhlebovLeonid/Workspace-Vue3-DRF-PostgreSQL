import { currentLocale } from '@/utils/locale'

export function toggleInArray<T>(items: T[], value: T): T[] {
  return items.includes(value) ? items.filter((item) => item !== value) : [...items, value]
}

export function sortByNickname<T extends { nickname: string }>(items: T[]): T[] {
  const locale = currentLocale()
  return [...items].sort((a, b) => a.nickname.localeCompare(b.nickname, locale))
}
