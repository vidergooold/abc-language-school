import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import Enroll from '@/pages/Enroll.vue'
import Testing from '@/pages/Testing.vue'
import Jobs from '@/pages/Jobs.vue'
import Clients from '@/pages/Clients.vue'
import Organization from '@/pages/Organization.vue'

import AccountLayout from '@/components/layout/AccountLayout.vue'
import Profile from '@/pages/account/Profile.vue'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/courses', component: Courses },
    { path: '/enroll', component: Enroll },
    { path: '/testing', component: Testing },
    { path: '/jobs', component: Jobs },
    { path: '/clients', component: Clients },
    { path: '/organization', component: Organization },
    { path: '/login', component: Login },
    { path: '/register', component: Register },

    {
      path: '/account',
      component: AccountLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          component: Profile,
        },
      ],
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
