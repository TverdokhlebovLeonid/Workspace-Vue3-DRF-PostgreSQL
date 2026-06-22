<script setup lang="ts">
import { computed, useId, useSlots } from 'vue'

defineOptions({ inheritAttrs: false })
const props = defineProps<{
  label?: string
  type?: string
  placeholder?: string
  error?: string
  valid?: boolean
  required?: boolean
  size?: 'md' | 'sm'
}>()
const model = defineModel<string | number>()
const id = useId()
const slots = useSlots()
const hasLeading = computed(() => Boolean(slots.leading))
const inputPadding = computed(() => {
  const left = hasLeading.value ? 'pl-10' : 'pl-4'
  const right = props.valid && !props.error ? 'pr-10' : 'pr-4'
  return [left, right]
})
</script>
<template>
  <div
    class="flex flex-col gap-1.5"
    v-bind="$attrs"
  >
    <label
      v-if="label"
      :for="id"
      class="text-sm font-medium text-ink"
    >
      {{ label }}
      <span
        v-if="required"
        class="text-red-500"
      >
        *
      </span>
    </label>
    <div class="relative">
      <span
        v-if="hasLeading"
        class="pointer-events-none absolute inset-y-0 left-3 flex items-center"
        aria-hidden="true"
      >
        <slot name="leading" />
      </span>
      <input
        :id="id"
        v-model="model"
        :type="type || 'text'"
        :placeholder="placeholder"
        class="w-full rounded-xl border bg-white py-2.5 text-ink outline-none transition placeholder:text-muted/60 focus:ring-2"
        :class="[
          inputPadding,
          size === 'sm' && 'text-sm',
          error
            ? 'border-red-400 focus:border-red-500 focus:ring-red-100'
            : valid
              ? 'border-brand-400 focus:border-brand-500 focus:ring-brand-100'
              : 'border-neutral-300 focus:border-brand-500 focus:ring-brand-100'
        ]"
      />
      <span
        v-if="valid && !error"
        class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-brand-600"
        aria-hidden="true"
      >
        ✓
      </span>
    </div>
    <p
      v-if="error"
      class="text-xs text-red-600"
    >
      {{ error }}
    </p>
  </div>
</template>
