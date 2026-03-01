import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'  
import Login from '@/pages/Login.vue'
import AccountLayout from '@/components/layout/AccountLayout.vue'
import Profile from '@/pages/account/Profile.vue'
import { useAuthStore } from '@/stores/auth'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/courses', component: Courses },
    { path: '/login', component: Login }, 
  ],
})
