import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue' // ← добавляем

import AccountLayout from '@/components/layout/AccountLayout.vue'
import Profile from '@/pages/account/Profile.vue'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/courses', component: Courses },
    { path: '/login', component: Login },
    { path: '/register', component: Register }, // ← маршрут регистрации
    {
      path: '/account',
      component: AccountLayout,
      meta: { requiresAuth: true },
      children: [{ path: '', component: Profile }],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return '/login'
  }
})

export default router
