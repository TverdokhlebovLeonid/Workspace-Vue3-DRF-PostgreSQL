<script setup lang="ts">
import UiTable from '@/components/ui/UiTable.vue'
import type { ScheduleGridWeek } from '@/types/schedules'
import { useI18n } from 'vue-i18n'

defineProps<{
  weeks: ScheduleGridWeek[]
  loadingHistory?: boolean
}>()
const emit = defineEmits<{
  scroll: [event: Event]
}>()
const { t } = useI18n()
</script>
<template>
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
          week.is_past ? 'border-neutral-300 bg-neutral-50/80' : 'border-neutral-200 bg-white'
        "
      >
        <UiTable :week="week" />
      </section>
    </div>
  </div>
</template>
