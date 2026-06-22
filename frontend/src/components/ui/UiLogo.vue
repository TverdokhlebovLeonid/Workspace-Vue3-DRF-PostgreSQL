<script setup lang="ts">
import { computed } from 'vue'

type Size = 'sm' | 'md'
const props = withDefaults(
  defineProps<{
    label?: string
    size?: Size
    centered?: boolean
  }>(),
  {
    label: 'Company',
    size: 'md',
    centered: false
  }
)
const sizeClasses: Record<Size, string> = {
  sm: 'rounded-xl px-3 py-1.5 text-sm',
  md: 'rounded-2xl px-5 py-2.5 text-lg shadow-soft'
}
const classes = computed(() => [
  'w-fit bg-brand-600 font-bold text-white',
  sizeClasses[props.size],
  props.centered && 'mx-auto'
])
</script>
<template>
  <div :class="classes">
    {{ label }}
  </div>
</template>
