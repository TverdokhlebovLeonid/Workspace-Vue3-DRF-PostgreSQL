<script setup lang="ts">
import IconLogOut from '@/components/icon/LogOut.vue'
import UiButton from '@/components/ui/UiButton.vue'
import UiButtonIcon from '@/components/ui/UiButtonIcon.vue'
import UiContainer from '@/components/ui/UiContainer.vue'
import UiLogo from '@/components/ui/UiLogo.vue'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

type NavItem = {
  labelKey: 'nav.schedule' | 'nav.profile' | 'nav.documents' | 'nav.locations' | 'nav.employees'
  to: string
  routeName: string
  adminOnly?: boolean
}
const navItems: NavItem[] = [
  { labelKey: 'nav.schedule', to: '/schedule', routeName: 'schedule' },
  { labelKey: 'nav.profile', to: '/profile', routeName: 'profile' },
  { labelKey: 'nav.documents', to: '/documents', routeName: 'documents' },
  {
    labelKey: 'nav.locations',
    to: '/admin/locations',
    routeName: 'admin-locations',
    adminOnly: true
  },
  {
    labelKey: 'nav.employees',
    to: '/admin/employees',
    routeName: 'admin-employees',
    adminOnly: true
  }
]
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const visibleNavItems = computed(() =>
  navItems.filter((item) => !item.adminOnly || authStore.isAdmin)
)
async function handleLogout() {
  await authStore.logout()
  await router.replace({ name: 'login' })
}
</script>
<template>
  <div class="flex min-h-screen flex-col bg-neutral-50">
    <header class="border-b border-neutral-200/80 bg-white/90 backdrop-blur">
      <UiContainer class="flex min-h-14 flex-wrap items-center justify-between gap-3 py-2">
        <div class="flex min-w-0 items-center gap-3">
          <UiLogo size="sm" />
          <div class="min-w-0">
            <p class="truncate font-semibold text-ink">
              {{ authStore.displayName }}
            </p>
            <p class="text-xs text-muted">{{ t('app.name') }}</p>
          </div>
        </div>
        <nav class="flex flex-wrap items-center gap-2">
          <UiButton
            v-for="item in visibleNavItems"
            :key="item.routeName"
            :label="t(item.labelKey)"
            variant="ghost"
            size="sm"
            :to="item.to"
            :active="route.name === item.routeName"
          />
          <UiButtonIcon
            :label="t('nav.logout')"
            variant="neutral"
            size="sm"
            @click="handleLogout"
          >
            <IconLogOut class="size-4" />
          </UiButtonIcon>
        </nav>
      </UiContainer>
    </header>
    <main class="flex-1 py-4">
      <RouterView />
    </main>
  </div>
</template>
