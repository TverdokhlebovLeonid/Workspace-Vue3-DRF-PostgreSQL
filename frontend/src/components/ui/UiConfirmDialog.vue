<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiModal from '@/components/ui/UiModal.vue'
import { useConfirm } from '@/composables/useConfirm'
import { computed } from 'vue'

const { state, accept, reject } = useConfirm()
const open = computed({
  get: () => state.open,
  set: (value) => {
    if (!value) reject()
  }
})
</script>
<template>
  <UiModal
    v-model="open"
    :title="state.title"
    max-width="max-w-md"
  >
    <p class="text-sm leading-relaxed text-muted">
      {{ state.message }}
    </p>
    <template #footer>
      <div class="flex flex-wrap justify-end gap-3">
        <UiButton
          variant="ghost"
          :label="state.cancelLabel"
          :disabled="state.loading"
          @click="reject"
        />
        <UiButton
          :variant="state.variant"
          :label="state.confirmLabel"
          :loading="state.loading"
          @click="accept"
        />
      </div>
    </template>
  </UiModal>
</template>
