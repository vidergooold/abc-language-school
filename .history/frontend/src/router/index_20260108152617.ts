import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'   // ← ДОБАВИТЬ

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/courses', component: Courses }, 
  ],
})
