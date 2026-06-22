<script setup lang="ts">
import type { ScheduleGridCell, ScheduleGridRow, ScheduleGridWeek } from '@/types/schedules'
import { isWeekend } from '@/utils/schedule'
import { useI18n } from 'vue-i18n'

defineProps<{
  week: ScheduleGridWeek
}>()
defineSlots<{
  cell(props: {
    cell: ScheduleGridCell
    row: ScheduleGridRow
    dayIndex: number
    week: ScheduleGridWeek
    weekend: boolean
    isPast: boolean
  }): unknown
}>()
const { t } = useI18n()
</script>
<template>
  <table class="min-w-[720px] w-full border-collapse text-sm">
    <thead>
      <tr
        class="border-b border-neutral-200"
        :class="week.is_past ? 'bg-neutral-100' : 'bg-neutral-50'"
      >
        <th
          class="sticky left-0 z-10 min-w-28 border-r border-neutral-200 px-3 py-2 text-left font-semibold text-ink"
          :class="week.is_past ? 'bg-neutral-100' : 'bg-neutral-50'"
        >
          {{ t('schedule.locationColumn') }}
        </th>
        <th
          v-for="day in week.days"
          :key="day.date"
          class="min-w-22 px-2 py-2 text-center font-medium"
          :class="isWeekend(day.weekday) && 'bg-[#ba002b]/5'"
        >
          <span class="block text-xs text-muted">
            <span :class="isWeekend(day.weekday) && 'text-[#ba002b]'">
              {{ day.weekday_label }}
            </span>
          </span>
          <span
            class="block"
            :class="week.is_past ? 'text-neutral-600' : 'text-brand-600'"
          >
            {{ day.display }}
          </span>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="row in week.rows"
        :key="`${week.week_start}-${row.location.id}`"
        class="border-b border-neutral-100 last:border-b-0"
      >
        <th
          scope="row"
          class="sticky left-0 z-10 border-r border-neutral-200 px-3 py-2 text-left font-medium text-ink"
          :class="week.is_past ? 'bg-neutral-50' : 'bg-white'"
        >
          {{ row.location.name }}
        </th>
        <template
          v-for="(cell, dayIndex) in row.cells"
          :key="cell.date"
        >
          <slot
            name="cell"
            :cell="cell"
            :row="row"
            :day-index="dayIndex"
            :week="week"
            :weekend="isWeekend(week.days[dayIndex]?.weekday ?? 0)"
            :is-past="Boolean(week.is_past)"
          >
            <td
              class="px-2 py-2 text-center"
              :class="[
                week.is_past ? 'text-neutral-500' : 'text-ink',
                isWeekend(week.days[dayIndex]?.weekday ?? 0) && 'bg-[#ba002b]/5'
              ]"
            >
              {{ cell.nickname || t('schedule.emptyCell') }}
            </td>
          </slot>
        </template>
      </tr>
    </tbody>
  </table>
</template>
