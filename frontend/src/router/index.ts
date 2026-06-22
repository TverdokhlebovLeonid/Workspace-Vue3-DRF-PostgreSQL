import { adminGuard } from '@/router/guards/adminGuard'
import { authGuard } from '@/router/guards/authGuard'
import { i18n } from '@/i18n'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { titleKey: 'login.submit', guestOnly: true }
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: { name: 'schedule' }
        },
        {
          path: 'schedule',
          name: 'schedule',
          component: () => import('@/views/ScheduleView.vue'),
          meta: { titleKey: 'nav.schedule' }
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { titleKey: 'nav.profile' }
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('@/views/DocumentsView.vue'),
          meta: { titleKey: 'nav.documents' }
        },
        {
          path: 'admin/locations',
          name: 'admin-locations',
          component: () => import('@/views/admin/LocationsAdminView.vue'),
          meta: { titleKey: 'nav.locations', requiresAdmin: true }
        },
        {
          path: 'admin/employees',
          name: 'admin-employees',
          component: () => import('@/views/admin/EmployeesAdminView.vue'),
          meta: { titleKey: 'nav.employees', requiresAdmin: true }
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: (to) => ({
        name: 'schedule',
        replace: true,
        query: to.query,
        hash: to.hash
      })
    }
  ]
})
router.beforeEach(async (to) => {
  const titleKey = typeof to.meta.titleKey === 'string' ? to.meta.titleKey : 'app.name'
  document.title = `${i18n.global.t(titleKey)} | ${i18n.global.t('app.name')}`
  if (to.matched.some((record) => record.meta.requiresAdmin)) {
    return adminGuard(to)
  }
  return authGuard(to)
})
export default router
