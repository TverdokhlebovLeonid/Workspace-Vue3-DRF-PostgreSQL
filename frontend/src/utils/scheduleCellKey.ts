export type CellKey = string

export function makeCellKey(date: string, locationId: string): CellKey {
  return `${date}|${locationId}`
}

export function parseCellKey(key: CellKey): { date: string; locationId: string } {
  const [date, locationId] = key.split('|')
  return { date: date ?? '', locationId: locationId ?? '' }
}
