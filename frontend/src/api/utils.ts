export type Paginated<T> = { results?: T[] } | T[]

export function unwrapList<T>(data: Paginated<T>): T[] {
  return Array.isArray(data) ? data : (data.results ?? [])
}
