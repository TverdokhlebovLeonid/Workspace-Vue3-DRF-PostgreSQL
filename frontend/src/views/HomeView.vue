<script setup lang="ts">
import UiButton from '@/components/ui/UiButton.vue'
import UiCard from '@/components/ui/UiCard.vue'
import UiContainer from '@/components/ui/UiContainer.vue'
import UiLogo from '@/components/ui/UiLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
async function handleLogout() {
  await authStore.logout()
  await router.replace({ name: 'login' })
}
</script>
<template>
  <div class="min-h-screen bg-neutral-50">
    <header class="border-b border-neutral-200/80 bg-white/90 backdrop-blur">
      <UiContainer class="flex h-16 items-center justify-between">
        <div class="flex items-center gap-3">
          <UiLogo size="sm" />
          <span class="font-semibold text-ink">Workspace</span>
        </div>
        <UiButton
          label="Выйти"
          variant="secondary"
          size="sm"
          @click="handleLogout"
        />
      </UiContainer>
    </header>
    <main class="py-12">
      <UiContainer>
        <UiCard class="max-w-2xl">
          <p class="text-sm font-medium uppercase tracking-wide text-brand-600">Авторизован</p>
          <h1 class="mt-2 text-3xl font-bold text-ink">Привет, {{ authStore.username }}!</h1>
          <p class="mt-3 text-muted">
            Роль:
            <span class="font-semibold text-ink">{{ authStore.role }}</span>
          </p>
        </UiCard>
      </UiContainer>
    </main>
  </div>
</template>
