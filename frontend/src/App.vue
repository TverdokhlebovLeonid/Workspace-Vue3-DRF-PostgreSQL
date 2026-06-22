<script setup lang="ts">
import UiConfirmDialog from '@/components/ui/UiConfirmDialog.vue'
import NotificationBox from '@/components/ui/Notification/NotificationBox.vue'
import { RouterView } from 'vue-router'
</script>
<template>
  <RouterView />
  <NotificationBox />
  <UiConfirmDialog />
</template>
