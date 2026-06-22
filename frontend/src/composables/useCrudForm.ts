import { useNotificationStore } from '@/stores/notification'
import type { EntityId } from '@/types/id'
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

type CrudAction = 'save' | 'create' | 'delete'

export type CrudFormConfig<TItem, TPayload> = {
  getId: (item: TItem) => EntityId
  resetForm: () => void
  fillForm: (item: TItem) => void
  snapshot: () => unknown
  buildPayload: () => TPayload
  validate?: (isEditing: boolean) => string | null
  create: (payload: TPayload) => Promise<unknown>
  update: (id: EntityId, payload: TPayload) => Promise<unknown>
  remove: (item: TItem) => Promise<unknown>
  reload: () => Promise<void>
  confirmDelete: (item: TItem) => Promise<boolean>
  errorText: (action: CrudAction) => string
}

export function useCrudForm<TItem, TPayload>(config: CrudFormConfig<TItem, TPayload>) {
  const { t } = useI18n()
  const notificationStore = useNotificationStore()

  const formVisible = ref(false)
  const editingId = ref<EntityId | null>(null)
  const saving = ref(false)
  const errorMessage = ref('')
  const initialSnapshot = ref<unknown>(null)

  const isEditing = computed(() => editingId.value !== null)
  const hasFormChanges = computed(() => {
    if (initialSnapshot.value === null) return false
    return JSON.stringify(config.snapshot()) !== JSON.stringify(initialSnapshot.value)
  })

  function openCreateForm() {
    config.resetForm()
    editingId.value = null
    errorMessage.value = ''
    formVisible.value = true
    initialSnapshot.value = config.snapshot()
  }

  function openEditForm(item: TItem) {
    config.fillForm(item)
    editingId.value = config.getId(item)
    errorMessage.value = ''
    formVisible.value = true
    initialSnapshot.value = config.snapshot()
  }

  function closeForm() {
    formVisible.value = false
    initialSnapshot.value = null
    config.resetForm()
    editingId.value = null
    errorMessage.value = ''
  }

  async function handleSubmit() {
    const validationError = config.validate?.(isEditing.value) ?? null
    if (validationError) {
      errorMessage.value = validationError
      return
    }
    saving.value = true
    errorMessage.value = ''
    const payload = config.buildPayload()
    try {
      if (editingId.value) {
        await config.update(editingId.value, payload)
        notificationStore.add({ text: t('common.updateSuccess'), type: 'success' })
      } else {
        await config.create(payload)
        notificationStore.add({ text: t('common.createSuccess'), type: 'success' })
      }
      await config.reload()
      closeForm()
    } catch {
      errorMessage.value = config.errorText(isEditing.value ? 'save' : 'create')
    } finally {
      saving.value = false
    }
  }

  async function handleDelete(item: TItem) {
    const ok = await config.confirmDelete(item)
    if (!ok) return
    if (editingId.value === config.getId(item)) closeForm()
    errorMessage.value = ''
    try {
      await config.remove(item)
      await config.reload()
      notificationStore.add({ text: t('common.deleteSuccess'), type: 'success' })
    } catch {
      errorMessage.value = config.errorText('delete')
    }
  }

  return {
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
  }
}
