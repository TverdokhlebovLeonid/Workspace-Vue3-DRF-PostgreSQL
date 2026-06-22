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
import { useConfirm } from '@/composables/useConfirm'
import { useCrudForm } from '@/composables/useCrudForm'
import type { Employee, EmployeePayload, Location, WorkRule } from '@/types/schedules'
import type { EntityId } from '@/types/id'
import { sortByNickname, toggleInArray } from '@/utils/collections'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { confirm } = useConfirm()
const employees = ref<Employee[]>([])
const locations = ref<Location[]>([])
const workRules = ref<WorkRule[]>([])
const loading = ref(true)
const form = reactive<EmployeePayload & { password: string }>({
  last_name: '',
  first_name: '',
  nickname: '',
  email: '',
  phone: '',
  location_ids: [],
  work_rule_ids: [],
  cycle_start_date: '',
  is_active: true,
  password: ''
})
const sortedEmployees = computed(() => sortByNickname(employees.value))
function resetForm() {
  form.last_name = ''
  form.first_name = ''
  form.nickname = ''
  form.email = ''
  form.phone = ''
  form.location_ids = []
  form.work_rule_ids = []
  form.cycle_start_date = ''
  form.is_active = true
  form.password = ''
}
function fillForm(employee: Employee) {
  form.last_name = employee.last_name
  form.first_name = employee.first_name
  form.nickname = employee.nickname
  form.email = employee.email
  form.phone = employee.phone
  form.location_ids = employee.locations.map((item) => item.id)
  form.work_rule_ids = employee.work_rules.map((item) => item.id)
  form.cycle_start_date = employee.cycle_start_date ?? ''
  form.is_active = employee.is_active
  form.password = ''
}
function toggleLocation(id: EntityId) {
  form.location_ids = toggleInArray(form.location_ids, id)
}
function toggleWorkRule(id: EntityId) {
  form.work_rule_ids = toggleInArray(form.work_rule_ids, id)
}
function buildPayload(): EmployeePayload {
  const payload: EmployeePayload = {
    last_name: form.last_name.trim(),
    first_name: form.first_name.trim(),
    nickname: form.nickname.trim(),
    email: (form.email ?? '').trim(),
    phone: (form.phone ?? '').trim(),
    location_ids: [...form.location_ids],
    work_rule_ids: [...form.work_rule_ids],
    cycle_start_date: form.cycle_start_date || undefined,
    is_active: form.is_active ?? true
  }
  const password = form.password.trim()
  if (password) {
    payload.password = password
  }
  return payload
}
function snapshotForm() {
  return {
    last_name: form.last_name.trim(),
    first_name: form.first_name.trim(),
    nickname: form.nickname.trim(),
    email: (form.email ?? '').trim(),
    phone: (form.phone ?? '').trim(),
    location_ids: [...form.location_ids].sort((a, b) => a.localeCompare(b)),
    work_rule_ids: [...form.work_rule_ids].sort((a, b) => a.localeCompare(b)),
    cycle_start_date: form.cycle_start_date ?? '',
    is_active: form.is_active ?? true,
    password: form.password.trim()
  }
}
function validateForm(isEditing: boolean): string | null {
  if (!form.last_name.trim() || !form.first_name.trim() || !form.nickname.trim()) {
    return t('employees.requiredError')
  }
  if (!isEditing && form.password.trim().length < 8) {
    return t('employees.passwordRequired')
  }
  if (isEditing && form.password.trim() && form.password.trim().length < 8) {
    return t('employees.passwordTooShort')
  }
  return null
}
async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const [employeesData, locationsData, rulesData] = await Promise.all([
      schedulesApi.getEmployees(),
      schedulesApi.getLocations(),
      schedulesApi.getWorkRules()
    ])
    employees.value = employeesData
    locations.value = locationsData
    workRules.value = rulesData
  } catch {
    errorMessage.value = t('employees.loadError')
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
} = useCrudForm<Employee, EmployeePayload>({
  getId: (employee) => employee.id,
  resetForm,
  fillForm,
  snapshot: snapshotForm,
  buildPayload,
  validate: validateForm,
  create: (payload) => schedulesApi.createEmployee(payload),
  update: (id, payload) => schedulesApi.updateEmployee(id, payload),
  remove: (employee) => schedulesApi.deleteEmployee(employee.id),
  reload: loadData,
  confirmDelete: (employee) =>
    confirm({
      message: t('employees.deleteConfirm', { nickname: employee.nickname }),
      confirmLabel: t('common.delete')
    }),
  errorText: (action) =>
    action === 'delete'
      ? t('employees.deleteError')
      : action === 'save'
        ? t('employees.saveError')
        : t('employees.createError')
})
const formTitle = computed(() =>
  isEditing.value ? t('employees.editTitle') : t('employees.addTitle')
)
onMounted(loadData)
</script>
<template>
  <UiContainer class="max-w-3xl space-y-6">
    <div>
      <h1 class="text-xl font-bold text-ink">{{ t('employees.title') }}</h1>
      <p class="text-sm text-muted">{{ t('employees.subtitle') }}</p>
    </div>
    <UiCard>
      <h2 class="mb-4 font-semibold text-ink">{{ t('employees.list') }}</h2>
      <p
        v-if="loading"
        class="text-muted"
      >
        {{ t('employees.loading') }}
      </p>
      <ul
        v-else-if="sortedEmployees.length"
        class="divide-y divide-neutral-100"
      >
        <li
          v-for="employee in sortedEmployees"
          :key="employee.id"
          class="flex items-start justify-between gap-3 py-3"
          :class="
            editingId === employee.id && formVisible && 'rounded-lg bg-brand-50/60 -mx-2 px-2'
          "
        >
          <div class="min-w-0">
            <p class="font-medium text-ink">
              {{ employee.nickname }}
              <span class="font-normal text-muted">
                ({{ employee.last_name }} {{ employee.first_name }})
              </span>
            </p>
            <p class="text-sm text-muted">
              {{
                employee.locations.map((item) => item.name).join(', ') || t('employees.noLocations')
              }}
            </p>
            <p class="text-sm text-muted">
              {{
                employee.work_rules.map((item) => item.name).join(' · ') || t('employees.noRules')
              }}
            </p>
          </div>
          <div class="flex shrink-0 gap-2">
            <UiButtonIcon
              :label="t('employees.edit')"
              variant="brand"
              size="sm"
              @click="openEditForm(employee)"
            >
              <IconEdit class="size-4" />
            </UiButtonIcon>
            <UiButtonIcon
              :label="t('employees.delete')"
              variant="danger"
              size="sm"
              @click="handleDelete(employee)"
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
        {{ t('employees.empty') }}
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
        :label="t('employees.add')"
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
            :label="t('employees.close')"
            variant="neutral"
            size="sm"
            @click="closeForm"
          >
            <IconClose class="size-4" />
          </UiButtonIcon>
        </div>
        <div class="grid gap-4 sm:grid-cols-2">
          <UiInput
            v-model="form.last_name"
            :label="t('employees.lastName')"
            required
          />
          <UiInput
            v-model="form.first_name"
            :label="t('employees.firstName')"
            required
          />
        </div>
        <UiInput
          v-model="form.nickname"
          :label="t('employees.nickname')"
          :placeholder="t('employees.nicknamePlaceholder')"
          required
        />
        <UiInput
          v-model="form.password"
          :label="isEditing ? t('employees.passwordEdit') : t('employees.password')"
          :placeholder="
            isEditing ? t('employees.passwordEditPlaceholder') : t('employees.passwordPlaceholder')
          "
          type="password"
          autocomplete="new-password"
          :required="!isEditing"
        />
        <p class="text-xs text-muted">{{ t('employees.loginHint') }}</p>
        <div class="grid gap-4 sm:grid-cols-2">
          <UiInput
            v-model="form.email"
            :label="t('employees.email')"
            type="email"
          />
          <UiInput
            v-model="form.phone"
            :label="t('employees.phone')"
          />
        </div>
        <UiInput
          v-model="form.cycle_start_date"
          :label="t('employees.cycleStart')"
          type="date"
        />
        <label class="flex cursor-pointer items-center gap-2 text-sm text-ink">
          <input
            v-model="form.is_active"
            type="checkbox"
          />
          {{ t('employees.active') }}
        </label>
        <div>
          <p class="mb-2 text-sm font-medium text-ink">{{ t('employees.locations') }}</p>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="location in locations"
              :key="location.id"
              class="flex cursor-pointer items-center gap-2 rounded-lg border border-neutral-200 px-3 py-2 text-sm"
            >
              <input
                type="checkbox"
                :checked="form.location_ids.includes(location.id)"
                @change="toggleLocation(location.id)"
              />
              {{ location.name }}
            </label>
          </div>
        </div>
        <div>
          <p class="mb-2 text-sm font-medium text-ink">{{ t('employees.workRules') }}</p>
          <div class="space-y-2">
            <label
              v-for="rule in workRules"
              :key="rule.id"
              class="flex cursor-pointer items-start gap-2 rounded-lg border border-neutral-200 px-3 py-2 text-sm"
            >
              <input
                type="checkbox"
                class="mt-1"
                :checked="form.work_rule_ids.includes(rule.id)"
                @change="toggleWorkRule(rule.id)"
              />
              <span>
                <span class="font-medium text-ink">{{ rule.name }}</span>
                <span
                  v-if="rule.description"
                  class="mt-0.5 block text-muted"
                >
                  {{ rule.description }}
                </span>
              </span>
            </label>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <UiButton
            :label="isEditing ? t('employees.saveChanges') : t('employees.save')"
            variant="primary"
            :disabled="saving || !hasFormChanges"
            :loading="saving"
            @click="handleSubmit"
          />
          <UiButton
            :label="t('employees.cancel')"
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
