import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function setupRouterGuards(router: Router) {
  router.beforeEach((to, _from, next) => {
    const auth = useAuthStore()
    const role = auth.user?.role || ''
    const isAuthenticated = !!auth.token

    // Redirect authenticated users away from login/register
    if (to.meta.redirectIfAuth && isAuthenticated) {
      return next('/account')
    }

    // Require authentication
    if (to.meta.requiresAuth && !isAuthenticated) {
      return next({ path: '/login', query: { redirect: to.fullPath } })
    }

    // Require admin role
    if (to.meta.requiresAdmin && role !== 'admin') {
      return next('/account')
    }

    // Require staff role (admin or teacher)
    if (to.meta.requiresStaff && !['admin', 'teacher'].includes(role)) {
      return next('/account')
    }

    // Require specific roles
    if (to.meta.allowedRoles && Array.isArray(to.meta.allowedRoles)) {
      const allowed = to.meta.allowedRoles as string[]
      if (!allowed.includes(role)) {
        return next('/account')
      }
    }

    next()
  })
}

// Legacy named exports kept for compatibility (no longer used as beforeEnter)
export const checkAuth = () => {}
export const checkRole = () => () => {}
export const checkStaff = () => {}
export const checkAdmin = () => {}
export const redirectAuthenticated = () => {}
