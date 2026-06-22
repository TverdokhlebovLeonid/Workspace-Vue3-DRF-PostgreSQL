<script setup lang="ts">
import UiSpinner from '@/components/ui/UiSpinner.vue'
import UiTooltip from '@/components/ui/UiTooltip.vue'
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

type Variant =
  | 'neutral'
  | 'brand'
  | 'danger'
  | 'muted'
  | 'plain'
  | 'primary'
  | 'surface'
  | 'success'
type Size = 'sm' | 'md' | 'lg'
defineOptions({ inheritAttrs: false })
const props = withDefaults(
  defineProps<{
    variant?: Variant
    size?: Size
    type?: 'button' | 'submit' | 'reset'
    to?: string
    label: string
    disabled?: boolean
    loading?: boolean
    tooltipPlacement?: 'top' | 'bottom'
  }>(),
  {
    variant: 'neutral',
    size: 'md',
    type: 'button',
    disabled: false,
    loading: false,
    tooltipPlacement: 'bottom'
  }
)
const variantClasses: Record<Variant, string> = {
  neutral:
    'border border-neutral-200 bg-white text-muted hover:border-neutral-300 hover:bg-neutral-100 hover:text-ink',
  brand:
    'border border-brand-200 bg-white text-ink hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700',
  primary:
    'border border-brand-600 bg-brand-600 text-white shadow-soft hover:border-brand-700 hover:bg-brand-700',
  danger:
    'border border-red-200 bg-white text-muted hover:border-red-300 hover:bg-red-50 hover:text-red-600',
  muted:
    'border border-neutral-200 bg-neutral-50 text-muted hover:border-neutral-300 hover:bg-neutral-100 hover:text-ink',
  surface: 'border border-white/30 bg-white/10 text-white hover:border-white/50 hover:bg-white/20',
  success: 'border border-success bg-white text-success hover:border-success hover:bg-success/10',
  plain: 'shrink-0 opacity-80 transition hover:opacity-100'
}
const sizeClasses: Record<Size, string> = {
  sm: 'grid size-8 place-items-center rounded-lg',
  md: 'grid size-9 place-items-center rounded-lg',
  lg: 'grid size-11 place-items-center rounded-xl'
}
const classes = computed(() => [
  'cursor-pointer outline-none transition disabled:cursor-not-allowed disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-brand-200 focus-visible:ring-offset-1',
  variantClasses[props.variant],
  props.variant !== 'plain' && sizeClasses[props.size],
  props.variant !== 'plain' && 'relative'
])
</script>
<template>
  <UiTooltip
    :text="label"
    :placement="tooltipPlacement"
  >
    <RouterLink
      v-if="to"
      :to="to"
      :aria-label="label"
      :class="classes"
      v-bind="$attrs"
    >
      <slot />
    </RouterLink>
    <button
      v-else
      :type="type"
      :aria-label="label"
      :disabled="disabled || loading"
      :class="classes"
      v-bind="$attrs"
    >
      <UiSpinner
        v-if="loading"
        class="size-4"
      />
      <slot v-else />
    </button>
  </UiTooltip>
</template>
