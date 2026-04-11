import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Проверка доступа к маршрутам на основе роли пользователя
 */
export function setupRouterGuards(router: any) {
  router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    const auth = useAuthStore()

    // 1. Проверка аутентификации
    if (to.meta.requiresAuth && !auth.isAuthenticated) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }

    // 2. Проверка роли admin
    if (to.meta.requiresAdmin && auth.user?.role !== 'admin') {
      return next('/account')
    }

    // 3. Проверка роли staff (сотрудник/преподаватель)
    if (to.meta.requiresStaff && !['admin', 'teacher', 'manager'].includes(auth.user?.role || '')) {
      return next('/login')
    }

    // 4. Проверка allowedRoles (гибкая проверка ролей)
    if (to.meta.allowedRoles && Array.isArray(to.meta.allowedRoles)) {
      const allowed = to.meta.allowedRoles as string[]
      if (!allowed.includes(auth.user?.role || '')) {
        return next('/account')
      }
    }

    // 5. Редирект авторизованных с /login и /register
    if ((to.path === '/login' || to.path === '/register') && auth.isAuthenticated) {
      return next('/account')
    }

    next()
  })
}
