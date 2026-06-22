<script setup lang="ts">
import usersApi from '@/api/users'
import LanguageSwitcher from '@/components/ui/LanguageSwitcher.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiContainer from '@/components/ui/UiContainer.vue'
import UiInput from '@/components/ui/UiInput.vue'
import { useNotificationStore } from '@/stores/notification'
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const notificationStore = useNotificationStore()
const saving = ref(false)
const errorMessage = ref('')
const form = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
type PasswordFieldKey = keyof typeof form
const passwordFields: {
  key: PasswordFieldKey
  labelKey: 'profile.currentPassword' | 'profile.newPassword' | 'profile.confirmPassword'
  autocomplete: string
}[] = [
  {
    key: 'current_password',
    labelKey: 'profile.currentPassword',
    autocomplete: 'current-password'
  },
  {
    key: 'new_password',
    labelKey: 'profile.newPassword',
    autocomplete: 'new-password'
  },
  {
    key: 'confirm_password',
    labelKey: 'profile.confirmPassword',
    autocomplete: 'new-password'
  }
]
const initialSnapshot = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const hasFormChanges = computed(
  () =>
    form.current_password !== initialSnapshot.value.current_password ||
    form.new_password !== initialSnapshot.value.new_password ||
    form.confirm_password !== initialSnapshot.value.confirm_password
)
function resetForm() {
  form.current_password = ''
  form.new_password = ''
  form.confirm_password = ''
  initialSnapshot.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  }
  errorMessage.value = ''
}
async function handleSubmit() {
  if (!form.current_password.trim()) {
    errorMessage.value = t('profile.currentRequired')
    return
  }
  if (form.new_password.length < 8) {
    errorMessage.value = t('profile.newTooShort')
    return
  }
  if (form.new_password !== form.confirm_password) {
    errorMessage.value = t('profile.confirmMismatch')
    return
  }
  saving.value = true
  errorMessage.value = ''
  try {
    await usersApi.changePassword({
      current_password: form.current_password,
      new_password: form.new_password
    })
    notificationStore.add({ text: t('profile.success'), type: 'success' })
    resetForm()
  } catch {
    errorMessage.value = t('profile.saveError')
  } finally {
    saving.value = false
  }
}
</script>
<template>
  <UiContainer class="max-w-lg space-y-6">
    <div>
      <h1 class="text-xl font-bold text-ink">{{ t('profile.title') }}</h1>
      <p class="text-sm text-muted">{{ t('profile.subtitle') }}</p>
    </div>
    <UiCard class="space-y-4">
      <div class="flex items-center justify-between gap-4">
        <span class="text-sm font-medium text-ink">{{ t('profile.languageTitle') }}</span>
        <LanguageSwitcher />
      </div>
      <hr class="border-neutral-100" />
      <h2 class="font-semibold text-ink">{{ t('profile.passwordTitle') }}</h2>
      <UiInput
        v-for="field in passwordFields"
        :key="field.key"
        v-model="form[field.key]"
        :label="t(field.labelKey)"
        type="password"
        :autocomplete="field.autocomplete"
        required
      />
      <div class="flex flex-wrap gap-2">
        <UiButton
          :label="t('profile.save')"
          variant="primary"
          :disabled="saving || !hasFormChanges"
          :loading="saving"
          @click="handleSubmit"
        />
      </div>
      <p
        v-if="errorMessage"
        class="text-sm text-red-600"
      >
        {{ errorMessage }}
      </p>
    </UiCard>
  </UiContainer>
</template>
