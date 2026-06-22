<script setup lang="ts">
import schedulesApi from '@/api/schedules'
import ScheduleGrid from '@/components/schedules/ScheduleGrid.vue'
import ScheduleGridEditor from '@/components/schedules/ScheduleGridEditor.vue'
import IconRefresh from '@/components/icon/Refresh.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiButtonIcon from '@/components/ui/UiButtonIcon.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiContainer from '@/components/ui/UiContainer.vue'
import UiSpinner from '@/components/ui/UiSpinner.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useScheduleEditor } from '@/composables/useScheduleEditor'
import { useScheduleHistoryScroll } from '@/composables/useScheduleHistoryScroll'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import type { Employee, ScheduleGrid as ScheduleGridType } from '@/types/schedules'
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const { t } = useI18n()
const { confirm } = useConfirm()
const notificationStore = useNotificationStore()
const {
  weeks,
  dragOverKey,
  hasChanges,
  dirtyKeys,
  isDirty,
  handleDrop,
  loadFromGrid,
  commitSaved,
  resetChanges,
  buildSavePayload
} = useScheduleEditor()
const grid = ref<ScheduleGridType | null>(null)
const employees = ref<Employee[]>([])
const loading = ref(true)
const generating = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const currentWeeks = computed(() =>
  authStore.isAdmin && weeks.value.length ? weeks.value : (grid.value?.weeks ?? [])
)
const { displayWeeks, loadingHistory, resetHistory, onScroll } =
  useScheduleHistoryScroll(currentWeeks)
async function loadGrid() {
  loading.value = true
  errorMessage.value = ''
  resetHistory()
  try {
    const [gridData, employeesData] = await Promise.all([
      schedulesApi.getGrid(),
      authStore.isAdmin ? schedulesApi.getEmployees() : Promise.resolve([])
    ])
    grid.value = gridData
    loadFromGrid(gridData)
    employees.value = employeesData
  } catch {
    errorMessage.value = t('schedule.loadError')
  } finally {
    loading.value = false
  }
}
async function handleGenerate() {
  if (hasChanges.value) {
    const confirmed = await confirm({
      message: t('schedule.unsavedConfirm'),
      confirmLabel: t('schedule.regenerate'),
      variant: 'primary'
    })
    if (!confirmed) return
  }
  generating.value = true
  errorMessage.value = ''
  resetHistory()
  try {
    const result = await schedulesApi.generate()
    grid.value = result.grid
    loadFromGrid(result.grid)
    notificationStore.add({ text: t('schedule.regenerateSuccess'), type: 'success' })
  } catch {
    errorMessage.value = t('schedule.regenerateError')
  } finally {
    generating.value = false
  }
}
async function handleSave() {
  if (!hasChanges.value) return
  saving.value = true
  errorMessage.value = ''
  try {
    const result = await schedulesApi.saveChanges(buildSavePayload())
    grid.value = result.grid
    commitSaved(result.grid)
    resetHistory()
    notificationStore.add({ text: t('schedule.saveSuccess'), type: 'success' })
  } catch {
    errorMessage.value = t('schedule.saveError')
  } finally {
    saving.value = false
  }
}
function handleReset() {
  resetChanges()
}
function setDragOver(key: string | null) {
  dragOverKey.value = key
}
onMounted(loadGrid)
</script>
<template>
  <UiContainer>
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-xl font-bold text-ink">{{ t('schedule.title') }}</h1>
        <p
          v-if="grid"
          class="text-sm text-muted"
        >
          {{
            t('schedule.period', {
              year: grid.year,
              start: grid.current_start_date,
              end: grid.current_end_date,
              weeks: grid.weeks_count
            })
          }}
        </p>
        <p class="text-xs text-muted">{{ t('schedule.scrollHint') }}</p>
      </div>
      <UiButtonIcon
        v-if="authStore.isAdmin"
        :label="t('schedule.regenerate')"
        variant="primary"
        size="sm"
        :disabled="generating || loading || saving"
        @click="handleGenerate"
      >
        <IconRefresh class="size-4" />
      </UiButtonIcon>
    </div>
    <UiCard
      v-if="loading"
      class="flex items-center justify-center py-8"
    >
      <UiSpinner class="size-8 text-brand-600" />
    </UiCard>
    <UiCard
      v-else-if="errorMessage && !grid"
      class="py-8 text-center text-red-600"
    >
      {{ errorMessage }}
    </UiCard>
    <template v-else-if="grid && !loading">
      <div
        v-if="grid.weeks.length"
        class="mb-3 hidden rounded-lg border border-brand-100 bg-brand-50 px-3 py-2 text-sm text-brand-800 max-md:portrait:block"
      >
        {{ t('schedule.rotateHint') }}
      </div>
      <ScheduleGridEditor
        v-if="authStore.isAdmin && grid.weeks[0]?.rows.length"
        :weeks="displayWeeks"
        :employees="employees"
        :is-dirty="isDirty"
        :drag-over-key="dragOverKey"
        :loading-history="loadingHistory"
        @drop="handleDrop"
        @drag-over="setDragOver"
        @scroll="onScroll"
      />
      <ScheduleGrid
        v-else-if="grid.weeks.length"
        :weeks="displayWeeks"
        :loading-history="loadingHistory"
        @scroll="onScroll"
      />
      <UiCard
        v-if="!grid.weeks[0]?.rows.length"
        class="mt-4 py-6 text-center text-muted"
      >
        {{ t('schedule.empty') }}
      </UiCard>
      <p
        v-if="errorMessage"
        class="mt-4 text-sm text-red-600"
      >
        {{ errorMessage }}
      </p>
      <div
        v-if="authStore.isAdmin && hasChanges"
        class="pointer-events-none sticky bottom-4 z-20 mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-lg"
      >
        <div class="pointer-events-auto flex flex-wrap items-center justify-between gap-3">
          <p class="text-sm text-amber-900">
            {{ t('schedule.unsavedBanner', { count: dirtyKeys.length }) }}
          </p>
          <div class="flex flex-wrap gap-2">
            <UiButton
              :label="t('common.cancel')"
              variant="secondary"
              size="sm"
              :disabled="saving"
              @click="handleReset"
            />
            <UiButton
              :label="t('schedule.save')"
              variant="primary"
              size="sm"
              :loading="saving"
              @click="handleSave"
            />
          </div>
        </div>
      </div>
    </template>
  </UiContainer>
</template>
