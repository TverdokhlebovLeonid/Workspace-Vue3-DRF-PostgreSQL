<script setup lang="ts">
import schedulesApi from '@/api/schedules'
import IconClose from '@/components/icon/Close.vue'
import IconEdit from '@/components/icon/Edit.vue'
import IconPlus from '@/components/icon/Plus.vue'
import IconTrash from '@/components/icon/Trash.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiButtonIcon from '@/components/ui/UiButtonIcon.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiContainer from '@/components/ui/UiContainer.vue'
import UiInput from '@/components/ui/UiInput.vue'
import UiSelect from '@/components/ui/UiSelect.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useCrudForm } from '@/composables/useCrudForm'
import type { Location, LocationPayload } from '@/types/schedules'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { confirm } = useConfirm()
const locations = ref<Location[]>([])
const loading = ref(true)
const form = reactive<LocationPayload>({
  location_type: 'STORE',
  name: '',
  sort_order: 0,
  is_active: true
})
const typeOptions = computed(() => [
  { value: 'STORE', label: t('locations.typeStore') },
  { value: 'CASH_REGISTER', label: t('locations.typeCashRegister') }
])
const sortedLocations = computed(() =>
  [...locations.value].sort((a, b) => a.sort_order - b.sort_order || a.name.localeCompare(b.name))
)
function resetForm() {
  form.location_type = 'STORE'
  form.name = ''
  form.sort_order = 0
  form.is_active = true
}
function fillForm(location: Location) {
  form.location_type = location.location_type
  form.name = location.name
  form.sort_order = location.sort_order
  form.is_active = location.is_active
}
function buildPayload(): LocationPayload {
  return {
    location_type: form.location_type,
    name: form.name.trim(),
    sort_order: form.sort_order,
    is_active: form.is_active ?? true
  }
}
async function loadLocations() {
  loading.value = true
  errorMessage.value = ''
  try {
    locations.value = await schedulesApi.getLocations()
  } catch {
    errorMessage.value = t('locations.loadError')
  } finally {
    loading.value = false
  }
}
const {
  formVisible,
  editingId,
  saving,
  errorMessage,
  isEditing,
  hasFormChanges,
  openCreateForm,
  openEditForm,
  closeForm,
  handleSubmit,
  handleDelete
} = useCrudForm<Location, LocationPayload>({
  getId: (location) => location.id,
  resetForm,
  fillForm,
  snapshot: () => buildPayload(),
  buildPayload,
  validate: () => (form.name.trim() ? null : t('locations.nameRequired')),
  create: (payload) => schedulesApi.createLocation(payload),
  update: (id, payload) => schedulesApi.updateLocation(id, payload),
  remove: (location) => schedulesApi.deleteLocation(location.id),
  reload: loadLocations,
  confirmDelete: (location) =>
    confirm({
      message: t('locations.deleteConfirm', { name: location.name }),
      confirmLabel: t('common.delete')
    }),
  errorText: (action) =>
    action === 'delete'
      ? t('locations.deleteError')
      : action === 'save'
        ? t('locations.saveError')
        : t('locations.createError')
})
const formTitle = computed(() =>
  isEditing.value ? t('locations.editTitle') : t('locations.addTitle')
)
onMounted(loadLocations)
</script>
<template>
  <UiContainer class="max-w-3xl space-y-6">
    <div>
      <h1 class="text-xl font-bold text-ink">{{ t('locations.title') }}</h1>
      <p class="text-sm text-muted">{{ t('locations.subtitle') }}</p>
    </div>
    <UiCard>
      <h2 class="mb-4 font-semibold text-ink">{{ t('locations.list') }}</h2>
      <p
        v-if="loading"
        class="text-muted"
      >
        {{ t('locations.loading') }}
      </p>
      <ul
        v-else-if="sortedLocations.length"
        class="divide-y divide-neutral-100"
      >
        <li
          v-for="location in sortedLocations"
          :key="location.id"
          class="flex items-start justify-between gap-3 py-3"
          :class="
            editingId === location.id && formVisible && 'rounded-lg bg-brand-50/60 -mx-2 px-2'
          "
        >
          <div class="min-w-0">
            <p class="font-medium text-ink">
              {{ location.name }}
              <span
                v-if="!location.is_active"
                class="text-sm font-normal text-muted"
              >
                {{ t('locations.inactive') }}
              </span>
            </p>
            <p class="text-sm text-muted">
              {{
                t('locations.meta', {
                  type: location.location_type_label,
                  order: location.sort_order
                })
              }}
            </p>
          </div>
          <div class="flex shrink-0 gap-2">
            <UiButtonIcon
              :label="t('locations.edit')"
              variant="brand"
              size="sm"
              @click="openEditForm(location)"
            >
              <IconEdit class="size-4" />
            </UiButtonIcon>
            <UiButtonIcon
              :label="t('locations.delete')"
              variant="danger"
              size="sm"
              @click="handleDelete(location)"
            >
              <IconTrash class="size-4" />
            </UiButtonIcon>
          </div>
        </li>
      </ul>
      <p
        v-else
        class="text-muted"
      >
        {{ t('locations.empty') }}
      </p>
      <p
        v-if="errorMessage && !formVisible"
        class="mt-4 text-sm text-red-600"
      >
        {{ errorMessage }}
      </p>
    </UiCard>
    <div>
      <UiButtonIcon
        v-if="!formVisible"
        :label="t('locations.add')"
        variant="success"
        @click="openCreateForm"
      >
        <IconPlus class="size-4" />
      </UiButtonIcon>
      <UiCard
        v-else
        class="space-y-4"
      >
        <div class="flex items-center justify-between gap-3">
          <h2 class="font-semibold text-ink">{{ formTitle }}</h2>
          <UiButtonIcon
            :label="t('locations.close')"
            variant="neutral"
            size="sm"
            @click="closeForm"
          >
            <IconClose class="size-4" />
          </UiButtonIcon>
        </div>
        <UiSelect
          v-model="form.location_type"
          :label="t('locations.type')"
          :options="typeOptions"
          required
        />
        <UiInput
          v-model="form.name"
          :label="t('locations.name')"
          :placeholder="t('locations.namePlaceholder')"
          required
        />
        <UiInput
          v-model.number="form.sort_order"
          :label="t('locations.sortOrder')"
          type="number"
        />
        <label class="flex cursor-pointer items-center gap-2 text-sm text-ink">
          <input
            v-model="form.is_active"
            type="checkbox"
          />
          {{ t('locations.active') }}
        </label>
        <div class="flex flex-wrap gap-2">
          <UiButton
            :label="isEditing ? t('locations.saveChanges') : t('locations.save')"
            variant="primary"
            :disabled="saving || !hasFormChanges"
            :loading="saving"
            @click="handleSubmit"
          />
          <UiButton
            :label="t('locations.cancel')"
            variant="ghost"
            :disabled="saving"
            @click="closeForm"
          />
        </div>
        <p
          v-if="errorMessage"
          class="text-sm text-red-600"
        >
          {{ errorMessage }}
        </p>
      </UiCard>
    </div>
  </UiContainer>
</template>
