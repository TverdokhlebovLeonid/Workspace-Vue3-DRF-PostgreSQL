import type { CellKey } from '@/utils/scheduleCellKey'

export type DragPayload =
  | { type: 'cell'; key: CellKey }
  | { type: 'palette'; employee_id: string; nickname: string }

export const SCHEDULE_DRAG_MIME = 'application/x-workspace-schedule'

export function readDragPayload(event: DragEvent): DragPayload | null {
  const raw =
    event.dataTransfer?.getData(SCHEDULE_DRAG_MIME) || event.dataTransfer?.getData('text/plain')
  if (!raw) return null
  try {
    return JSON.parse(raw) as DragPayload
  } catch {
    return null
  }
}

export function writeDragPayload(
  event: DragEvent,
  payload: DragPayload,
  effectAllowed: DataTransfer['effectAllowed']
) {
  if (!event.dataTransfer) return
  const json = JSON.stringify(payload)
  event.dataTransfer.setData(SCHEDULE_DRAG_MIME, json)
  event.dataTransfer.setData('text/plain', json)
  event.dataTransfer.effectAllowed = effectAllowed
}

let dragPayloadStore: DragPayload | null = null

export function storeDragPayload(payload: DragPayload | null) {
  dragPayloadStore = payload
}

export function consumeDragPayload(event: DragEvent): DragPayload | null {
  const payload = readDragPayload(event) ?? dragPayloadStore
  dragPayloadStore = null
  return payload
}
