<script setup lang="ts">
import IconClose from '@/components/icon/Close.vue'
import UiButtonIcon from '@/components/ui/UiButtonIcon.vue'
import { lockBodyScroll, unlockBodyScroll } from '@/composables/useBodyScrollLock'
import { onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

withDefaults(
  defineProps<{
    title?: string
    maxWidth?: string
  }>(),
  {
    maxWidth: 'max-w-lg'
  }
)
const model = defineModel<boolean>({ required: true })
const { t } = useI18n()
function close() {
  model.value = false
}
function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') close()
}
watch(model, (open) => {
  if (typeof window === 'undefined') return
  if (open) lockBodyScroll()
  else unlockBodyScroll()
})
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  if (typeof window !== 'undefined' && model.value) unlockBodyScroll()
})
</script>
<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      leave-active-class="transition duration-150 ease-in"
      leave-to-class="opacity-0"
    >
      <div
        v-if="model"
        class="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-ink/50 p-4 backdrop-blur-sm"
        @click.self="close"
      >
        <Transition
          enter-active-class="transition duration-200 ease-out"
          enter-from-class="opacity-0 translate-y-4 scale-95"
          leave-active-class="transition duration-150 ease-in"
          leave-to-class="opacity-0 translate-y-4 scale-95"
          appear
        >
          <div
            v-if="model"
            class="relative w-full rounded-2xl bg-white shadow-2xl"
            :class="maxWidth"
            role="dialog"
            aria-modal="true"
          >
            <header
              v-if="title || $slots.header"
              class="flex items-center justify-between border-b border-neutral-100 px-6 py-4"
            >
              <slot name="header">
                <h2 class="text-lg font-semibold text-ink">{{ title }}</h2>
              </slot>
              <UiButtonIcon
                variant="neutral"
                size="sm"
                :label="t('common.close')"
                @click="close"
              >
                <IconClose class="size-5" />
              </UiButtonIcon>
            </header>
            <div class="px-6 py-5">
              <slot />
            </div>
            <footer
              v-if="$slots.footer"
              class="border-t border-neutral-100 px-6 py-4"
            >
              <slot name="footer" />
            </footer>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
