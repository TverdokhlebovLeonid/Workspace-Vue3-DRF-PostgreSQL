<script setup lang="ts">
import UiTable from '@/components/ui/UiTable.vue'
import { makeCellKey, type CellKey } from '@/utils/scheduleCellKey'
import {
  consumeDragPayload,
  storeDragPayload,
  writeDragPayload,
  type DragPayload
} from '@/utils/scheduleDrag'
import { sortEmployeesForPalette } from '@/utils/schedule'
import type { Employee, ScheduleGridWeek } from '@/types/schedules'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const props = defineProps<{
  weeks: ScheduleGridWeek[]
  employees: Employee[]
  isDirty: (key: CellKey) => boolean
  dragOverKey: CellKey | null
  loadingHistory?: boolean
}>()
const emit = defineEmits<{
  drop: [targetKey: CellKey, payload: DragPayload]
  dragOver: [key: CellKey | null]
  scroll: [event: Event]
}>()
const paletteEmployees = computed(() => sortEmployeesForPalette(props.employees))
const activeDrag = ref<DragPayload | null>(null)
const paletteOpen = ref(false)
const { t } = useI18n()
function isPastWeek(week: ScheduleGridWeek): boolean {
  return Boolean(week.is_past)
}
function finishDrag() {
  activeDrag.value = null
  storeDragPayload(null)
  emit('dragOver', null)
}
function onPaletteDragStart(event: DragEvent, employee: Employee) {
  if (!event.dataTransfer) return
  const payload: DragPayload = {
    type: 'palette',
    employee_id: employee.id,
    nickname: employee.nickname
  }
  activeDrag.value = payload
  storeDragPayload(payload)
  writeDragPayload(event, payload, 'copyMove')
}
function onCellDragStart(event: DragEvent, key: CellKey, isPast: boolean) {
  if (isPast || !event.dataTransfer) return
  const payload: DragPayload = { type: 'cell', key }
  activeDrag.value = payload
  storeDragPayload(payload)
  writeDragPayload(event, payload, 'move')
}
function onDragOver(event: DragEvent, key: CellKey, isPast: boolean) {
  if (isPast) return
  event.preventDefault()
  event.stopPropagation()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = activeDrag.value?.type === 'palette' ? 'copy' : 'move'
  }
  emit('dragOver', key)
}
function onDrop(event: DragEvent, targetKey: CellKey, isPast: boolean) {
  if (isPast) return
  event.preventDefault()
  event.stopPropagation()
  const payload = consumeDragPayload(event) ?? activeDrag.value
  finishDrag()
  if (!payload) return
  emit('drop', targetKey, payload)
}
function cellClasses(key: CellKey, weekend: boolean, isPast: boolean) {
  return [
    'min-h-[2.25rem] px-2 py-2 text-center transition-colors',
    isPast
      ? 'cursor-default text-neutral-500'
      : 'cursor-grab text-ink active:cursor-grabbing select-none',
    weekend && 'bg-[#ba002b]/5',
    !isPast && props.isDirty(key) && 'bg-amber-100 ring-2 ring-inset ring-amber-400 font-medium',
    !isPast && props.dragOverKey === key && 'bg-brand-50 ring-2 ring-inset ring-brand-400'
  ]
}
</script>
<template>
  <div
    class="space-y-4"
    @dragend="finishDrag"
  >
    <div class="rounded-xl border border-neutral-200 bg-white shadow-sm">
      <button
        type="button"
        class="flex w-full items-center justify-between gap-3 px-4 py-3 text-left"
        :aria-expanded="paletteOpen"
        @click="paletteOpen = !paletteOpen"
      >
        <span class="text-sm font-medium text-ink">{{ t('schedule.editorPaletteTitle') }}</span>
        <span
          class="text-muted transition-transform duration-200"
          :class="paletteOpen && 'rotate-180'"
          aria-hidden="true"
        >
          ▼
        </span>
      </button>
      <div
        v-show="paletteOpen"
        class="border-t border-neutral-100 px-4 pb-4 pt-3"
      >
        <p class="mb-3 text-xs text-muted">
          {{ t('schedule.editorPaletteHint') }}
        </p>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="employee in paletteEmployees"
            :key="employee.id"
            draggable="true"
            class="cursor-grab rounded-lg border border-brand-200 bg-brand-50 px-3 py-1.5 text-sm font-medium text-brand-800 active:cursor-grabbing"
            @dragstart="onPaletteDragStart($event, employee)"
          >
            {{ employee.nickname }}
          </div>
        </div>
      </div>
    </div>
    <div
      class="max-h-[min(70vh,42rem)] overflow-y-auto overflow-x-hidden rounded-xl border border-neutral-200 bg-white shadow-sm"
      @scroll="emit('scroll', $event)"
    >
      <div class="space-y-6 p-3">
        <div
          v-if="loadingHistory"
          class="flex items-center justify-center py-2 text-sm text-muted"
        >
          {{ t('schedule.loadingHistory') }}
        </div>
        <p
          v-if="weeks.some((week) => week.is_past)"
          class="rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-xs text-muted"
        >
          {{ t('schedule.historyHint') }}
        </p>
        <section
          v-for="week in weeks"
          :key="week.week_start"
          class="overflow-x-auto rounded-xl border shadow-sm"
          :class="
            isPastWeek(week) ? 'border-neutral-300 bg-neutral-50/80' : 'border-neutral-200 bg-white'
          "
        >
          <UiTable :week="week">
            <template #cell="{ cell, row, weekend, isPast }">
              <td
                :draggable="!isPast"
                :class="cellClasses(makeCellKey(cell.date, row.location.id), weekend, isPast)"
                @dragstart="
                  onCellDragStart($event, makeCellKey(cell.date, row.location.id), isPast)
                "
                @dragover="onDragOver($event, makeCellKey(cell.date, row.location.id), isPast)"
                @drop="onDrop($event, makeCellKey(cell.date, row.location.id), isPast)"
              >
                {{ cell.nickname || t('schedule.emptyCell') }}
              </td>
            </template>
          </UiTable>
        </section>
      </div>
    </div>
  </div>
</template>
