import type { ScheduleGrid, ScheduleGridCell, ScheduleGridWeek } from '@/types/schedules'
import { makeCellKey, parseCellKey, type CellKey } from '@/utils/scheduleCellKey'
import type { DragPayload } from '@/utils/scheduleDrag'
import { computed, ref, triggerRef } from 'vue'

function indexGridCells(weeks: ScheduleGridWeek[]): {
  cellIndex: Map<CellKey, ScheduleGridCell>
  snapshot: Map<CellKey, ScheduleGridCell>
} {
  const cellIndex = new Map<CellKey, ScheduleGridCell>()
  const snapshot = new Map<CellKey, ScheduleGridCell>()
  for (const week of weeks) {
    for (const row of week.rows) {
      const locationId = row.location.id
      for (const cell of row.cells) {
        const key = makeCellKey(cell.date, locationId)
        cellIndex.set(key, cell)
        snapshot.set(key, {
          date: cell.date,
          employee_id: cell.employee_id,
          nickname: cell.nickname
        })
      }
    }
  }
  return { cellIndex, snapshot }
}
export function useScheduleEditor() {
  const weeks = ref<ScheduleGridWeek[]>([])
  const cellIndex = ref<Map<CellKey, ScheduleGridCell>>(new Map())
  const original = ref<Map<CellKey, ScheduleGridCell>>(new Map())
  const dragOverKey = ref<CellKey | null>(null)
  const currentStartDate = ref('')
  function loadFromGrid(grid: ScheduleGrid) {
    weeks.value = structuredClone(grid.weeks)
    currentStartDate.value = grid.current_start_date
    const indexed = indexGridCells(weeks.value)
    cellIndex.value = indexed.cellIndex
    original.value = indexed.snapshot
  }
  function isPastCell(key: CellKey): boolean {
    if (!currentStartDate.value) return false
    const { date } = parseCellKey(key)
    return date < currentStartDate.value
  }
  function getCell(key: CellKey): ScheduleGridCell | undefined {
    return cellIndex.value.get(key)
  }
  function isDirty(key: CellKey): boolean {
    if (isPastCell(key)) return false
    const baseline = original.value.get(key)
    const current = getCell(key)
    if (!baseline || !current) return false
    return baseline.employee_id !== current.employee_id || baseline.nickname !== current.nickname
  }
  const dirtyKeys = computed(() => {
    const keys: CellKey[] = []
    for (const key of original.value.keys()) {
      if (isDirty(key)) keys.push(key)
    }
    return keys
  })
  const hasChanges = computed(() => dirtyKeys.value.length > 0)
  function swapCells(keyA: CellKey, keyB: CellKey) {
    if (keyA === keyB) return
    const cellA = getCell(keyA)
    const cellB = getCell(keyB)
    if (!cellA || !cellB) return
    const tempId = cellA.employee_id
    const tempNick = cellA.nickname
    cellA.employee_id = cellB.employee_id
    cellA.nickname = cellB.nickname
    cellB.employee_id = tempId
    cellB.nickname = tempNick
    triggerRef(weeks)
  }
  function replaceCell(key: CellKey, employeeId: string, nickname: string) {
    const cell = getCell(key)
    if (!cell) return
    cell.employee_id = employeeId
    cell.nickname = nickname
    triggerRef(weeks)
  }
  function handleDrop(targetKey: CellKey, payload: DragPayload) {
    if (isPastCell(targetKey)) return
    if (payload.type === 'palette') {
      replaceCell(targetKey, payload.employee_id, payload.nickname)
      return
    }
    if (payload.type === 'cell' && payload.key !== targetKey && !isPastCell(payload.key)) {
      swapCells(payload.key, targetKey)
    }
  }
  function resetChanges() {
    for (const [key, baseline] of original.value.entries()) {
      const cell = getCell(key)
      if (cell) {
        cell.employee_id = baseline.employee_id
        cell.nickname = baseline.nickname
      }
    }
    triggerRef(weeks)
  }
  function commitSaved(grid: ScheduleGrid) {
    loadFromGrid(grid)
  }
  function buildSavePayload() {
    return dirtyKeys.value.map((key) => {
      const cell = getCell(key)!
      const { date, locationId } = parseCellKey(key)
      return {
        date,
        location_id: locationId,
        employee_id: cell.employee_id
      }
    })
  }
  return {
    weeks,
    dragOverKey,
    hasChanges,
    dirtyKeys,
    loadFromGrid,
    commitSaved,
    resetChanges,
    buildSavePayload,
    isDirty,
    makeCellKey,
    handleDrop
  }
}
