<script setup lang="ts">
import documentsApi from '@/api/documents'
import schedulesApi from '@/api/schedules'
import IconDownload from '@/components/icon/Download.vue'
import IconTrash from '@/components/icon/Trash.vue'
import IconUpload from '@/components/icon/Upload.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiButtonIcon from '@/components/ui/UiButtonIcon.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiContainer from '@/components/ui/UiContainer.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import type { DocumentAccessEntry, DocumentItem } from '@/types/documents'
import type { EntityId } from '@/types/id'
import type { Employee } from '@/types/schedules'
import { sortByNickname, toggleInArray } from '@/utils/collections'
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const authStore = useAuthStore()
const { t } = useI18n()
const { confirm } = useConfirm()
const notificationStore = useNotificationStore()
const documents = ref<DocumentItem[]>([])
const employees = ref<Employee[]>([])
const loading = ref(true)
const uploading = ref(false)
const savingAccessId = ref<EntityId | null>(null)
const downloadingId = ref<EntityId | null>(null)
const errorMessage = ref('')
const uploadForm = reactive({
  title: ''
})
const accessByDocument = ref<Record<EntityId, EntityId[]>>({})
const savedAccessByDocument = ref<Record<EntityId, EntityId[]>>({})
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isAdmin = computed(() => authStore.isAdmin)
const sortedEmployees = computed(() => sortByNickname(employees.value))
function normalizeEmployeeIds(ids: EntityId[]): EntityId[] {
  return [...ids].sort()
}
function areEmployeeIdsEqual(left: EntityId[], right: EntityId[]): boolean {
  const normalizedLeft = normalizeEmployeeIds(left)
  const normalizedRight = normalizeEmployeeIds(right)
  return (
    normalizedLeft.length === normalizedRight.length &&
    normalizedLeft.every((id, index) => id === normalizedRight[index])
  )
}
function syncAccessState(items: DocumentItem[]) {
  const nextAccess: Record<EntityId, EntityId[]> = {}
  const nextSaved: Record<EntityId, EntityId[]> = {}
  for (const doc of items) {
    nextAccess[doc.id] = [...doc.employee_ids]
    nextSaved[doc.id] = [...doc.employee_ids]
  }
  accessByDocument.value = nextAccess
  savedAccessByDocument.value = nextSaved
}
function hasAccessChanges(documentId: EntityId): boolean {
  return !areEmployeeIdsEqual(
    accessByDocument.value[documentId] ?? [],
    savedAccessByDocument.value[documentId] ?? []
  )
}
function getAccessEntry(
  document: DocumentItem,
  employeeId: EntityId
): DocumentAccessEntry | undefined {
  return document.access_entries.find((entry) => entry.employee_id === employeeId)
}
function formatGrantedAt(iso: string): string {
  return new Intl.DateTimeFormat(authStore.language === 'ru' ? 'ru-RU' : 'en-GB', {
    dateStyle: 'short',
    timeStyle: 'short'
  }).format(new Date(iso))
}
function accessGrantedLabel(document: DocumentItem, employeeId: EntityId): string | null {
  const entry = getAccessEntry(document, employeeId)
  if (!entry) {
    return null
  }
  const date = formatGrantedAt(entry.granted_at)
  if (entry.granted_by_username) {
    return t('documents.accessGranted', {
      date,
      username: entry.granted_by_username
    })
  }
  return t('documents.accessGrantedUnknown', { date })
}
async function loadData() {
  loading.value = true
  errorMessage.value = ''
  try {
    const docs = await documentsApi.getDocuments()
    documents.value = docs
    syncAccessState(docs)
    if (isAdmin.value) {
      employees.value = await schedulesApi.getEmployees()
    }
  } catch {
    errorMessage.value = t('documents.loadError')
  } finally {
    loading.value = false
  }
}
function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] ?? null
}
function toggleEmployee(documentId: EntityId, employeeId: EntityId) {
  accessByDocument.value[documentId] = toggleInArray(
    accessByDocument.value[documentId] ?? [],
    employeeId
  )
}
async function handleUpload() {
  if (!uploadForm.title.trim()) {
    errorMessage.value = t('documents.titleRequired')
    return
  }
  if (!selectedFile.value) {
    errorMessage.value = t('documents.fileRequired')
    return
  }
  const ext = selectedFile.value.name.split('.').pop()?.toLowerCase() ?? ''
  if (!['png', 'jpg', 'jpeg'].includes(ext)) {
    errorMessage.value = t('documents.invalidFormat')
    return
  }
  uploading.value = true
  errorMessage.value = ''
  try {
    await documentsApi.uploadDocument(uploadForm.title, selectedFile.value)
    uploadForm.title = ''
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    await loadData()
    notificationStore.add({ text: t('common.createSuccess'), type: 'success' })
  } catch {
    errorMessage.value = t('documents.uploadError')
  } finally {
    uploading.value = false
  }
}
async function handleSaveAccess(document: DocumentItem) {
  savingAccessId.value = document.id
  errorMessage.value = ''
  try {
    const updated = await documentsApi.updateAccess(document.id, {
      employee_ids: accessByDocument.value[document.id] ?? []
    })
    documents.value = documents.value.map((item) => (item.id === updated.id ? updated : item))
    accessByDocument.value[updated.id] = [...updated.employee_ids]
    savedAccessByDocument.value[updated.id] = [...updated.employee_ids]
    notificationStore.add({ text: t('common.updateSuccess'), type: 'success' })
  } catch {
    errorMessage.value = t('documents.accessError')
  } finally {
    savingAccessId.value = null
  }
}
async function handleDelete(document: DocumentItem) {
  const ok = await confirm({
    message: t('documents.deleteConfirm', { title: document.title }),
    confirmLabel: t('common.delete')
  })
  if (!ok) return
  errorMessage.value = ''
  try {
    await documentsApi.deleteDocument(document.id)
    await loadData()
    notificationStore.add({ text: t('common.deleteSuccess'), type: 'success' })
  } catch {
    errorMessage.value = t('documents.deleteError')
  }
}
async function handleDownload(document: DocumentItem) {
  downloadingId.value = document.id
  errorMessage.value = ''
  try {
    await documentsApi.downloadDocument(document.id, document.file_name || 'document')
  } catch {
    errorMessage.value = t('documents.downloadError')
  } finally {
    downloadingId.value = null
  }
}
onMounted(loadData)
</script>
<template>
  <UiContainer class="max-w-3xl space-y-6">
    <div>
      <h1 class="text-xl font-bold text-ink">{{ t('documents.title') }}</h1>
      <p class="text-sm text-muted">
        {{ isAdmin ? t('documents.subtitleAdmin') : t('documents.subtitleUser') }}
      </p>
    </div>
    <UiCard
      v-if="isAdmin"
      class="space-y-4"
    >
      <h2 class="font-semibold text-ink">{{ t('documents.uploadTitle') }}</h2>
      <UiInput
        v-model="uploadForm.title"
        :label="t('documents.documentTitle')"
        required
      />
      <div>
        <p class="mb-2 text-sm font-medium text-ink">{{ t('documents.file') }}</p>
        <input
          ref="fileInput"
          type="file"
          accept=".png,.jpg,.jpeg,image/png,image/jpeg"
          class="block w-full text-sm text-muted file:mr-3 file:rounded-lg file:border-0 file:bg-neutral-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-ink"
          @change="onFileChange"
        />
        <p class="mt-1 text-xs text-muted">{{ t('documents.formatsHint') }}</p>
      </div>
      <UiButtonIcon
        :label="t('documents.upload')"
        variant="primary"
        :disabled="uploading"
        @click="handleUpload"
      >
        <IconUpload class="size-4" />
      </UiButtonIcon>
    </UiCard>
    <UiCard>
      <h2 class="mb-4 font-semibold text-ink">{{ t('documents.list') }}</h2>
      <p
        v-if="loading"
        class="text-muted"
      >
        {{ t('documents.loading') }}
      </p>
      <ul
        v-else-if="documents.length"
        class="divide-y divide-neutral-100"
      >
        <li
          v-for="document in documents"
          :key="document.id"
          class="space-y-3 py-4"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p class="font-medium text-ink">{{ document.title }}</p>
              <p class="text-sm text-muted">
                {{ document.file_name || t('documents.noFileName') }}
              </p>
            </div>
            <div class="flex shrink-0 flex-wrap gap-2">
              <UiButtonIcon
                v-if="document.can_download"
                :label="t('documents.download')"
                variant="brand"
                size="sm"
                :disabled="downloadingId === document.id"
                @click="handleDownload(document)"
              >
                <IconDownload class="size-4" />
              </UiButtonIcon>
              <UiButtonIcon
                v-if="isAdmin"
                :label="t('documents.delete')"
                variant="danger"
                size="sm"
                @click="handleDelete(document)"
              >
                <IconTrash class="size-4" />
              </UiButtonIcon>
            </div>
          </div>
          <div
            v-if="isAdmin"
            class="rounded-lg border border-neutral-200 p-3"
          >
            <p class="mb-2 text-sm font-medium text-ink">{{ t('documents.accessTitle') }}</p>
            <div class="flex flex-wrap gap-2">
              <label
                v-for="employee in sortedEmployees"
                :key="employee.id"
                class="flex min-w-28 cursor-pointer flex-col gap-1 rounded-lg border border-neutral-200 px-3 py-2 text-sm"
              >
                <span class="flex items-center gap-2">
                  <input
                    type="checkbox"
                    :checked="(accessByDocument[document.id] ?? []).includes(employee.id)"
                    @change="toggleEmployee(document.id, employee.id)"
                  />
                  {{ employee.nickname }}
                </span>
                <span
                  v-if="
                    (accessByDocument[document.id] ?? []).includes(employee.id) &&
                    accessGrantedLabel(document, employee.id)
                  "
                  class="pl-6 text-xs text-muted"
                >
                  {{ accessGrantedLabel(document, employee.id) }}
                </span>
              </label>
            </div>
            <UiButton
              class="mt-3"
              :label="t('documents.save')"
              variant="primary"
              size="sm"
              :disabled="!hasAccessChanges(document.id) || savingAccessId === document.id"
              :loading="savingAccessId === document.id"
              @click="handleSaveAccess(document)"
            />
          </div>
        </li>
      </ul>
      <p
        v-else
        class="text-muted"
      >
        {{ t('documents.empty') }}
      </p>
    </UiCard>
    <p
      v-if="errorMessage"
      class="text-sm text-red-600"
    >
      {{ errorMessage }}
    </p>
  </UiContainer>
</template>
