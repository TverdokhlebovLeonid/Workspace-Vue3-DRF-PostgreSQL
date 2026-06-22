import schedulesApi from '@/api/schedules'
import type { ScheduleGridWeek } from '@/types/schedules'
import { computed, nextTick, ref, type Ref } from 'vue'

export function useScheduleHistoryScroll(currentWeeks: Ref<ScheduleGridWeek[]>) {
  const historyWeeks = ref<ScheduleGridWeek[]>([])
  const loadingHistory = ref(false)
  const displayWeeks = computed(() => [...historyWeeks.value, ...currentWeeks.value])
  const earliestWeekStart = computed(
    () => historyWeeks.value[0]?.week_start ?? currentWeeks.value[0]?.week_start ?? null
  )
  function resetHistory() {
    historyWeeks.value = []
  }
  async function loadMoreHistory(scrollRoot?: HTMLElement | null) {
    if (loadingHistory.value || !earliestWeekStart.value) return
    const prevScrollHeight = scrollRoot?.scrollHeight ?? 0
    loadingHistory.value = true
    try {
      const chunk = await schedulesApi.getGridHistory(earliestWeekStart.value)
      historyWeeks.value = [...chunk.weeks, ...historyWeeks.value]
      if (scrollRoot) {
        await nextTick()
        scrollRoot.scrollTop += scrollRoot.scrollHeight - prevScrollHeight
      }
    } finally {
      loadingHistory.value = false
    }
  }
  async function onScroll(event: Event) {
    const el = event.target as HTMLElement | null
    if (!el || loadingHistory.value || el.scrollTop > 120) return
    await loadMoreHistory(el)
  }
  return {
    historyWeeks,
    displayWeeks,
    loadingHistory,
    resetHistory,
    loadMoreHistory,
    onScroll
  }
}
