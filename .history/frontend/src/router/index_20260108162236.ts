import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'  
import Login from '@/pages/Login.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/courses', component: Courses },
    { path: '/login', component: Login }, 
  ],
})
