import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import Enroll from '@/pages/Enroll.vue'
import Testing from '@/pages/Testing.vue'
import Jobs from '@/pages/Jobs.vue'

// Organization layout и подстраницы
import OrganizationLayout from '@/components/layout/OrganizationLayout.vue'
import OrgMain from '@/pages/organization/Main.vue'
import OrgStructure from '@/pages/organization/Structure.vue'
import OrgDocs from '@/pages/organization/Docs.vue'
import OrgEducation from '@/pages/organization/Education.vue'
import OrgManagement from '@/pages/organization/Management.vue'
import OrgStaff from '@/pages/organization/Staff.vue'
import OrgFacilities from '@/pages/organization/Facilities.vue'
import OrgServices from '@/pages/organization/Services.vue'
import OrgFinance from '@/pages/organization/Finance.vue'
import OrgVacancies from '@/pages/organization/Vacancies.vue'
import OrgInternational from '@/pages/organization/International.vue'

// Clients layout и подстраницы
import ClientsLayout from '@/components/layout/ClientsLayout.vue'
import ClientsImportant from '@/pages/clients/Important.vue'
import ClientsHolidays from '@/pages/clients/Holidays.vue'
import ClientsPayment from '@/pages/clients/Payment.vue'
import ClientsTax from '@/pages/clients/Tax.vue'

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
    { path: '/login', component: Login },
    { path: '/register', component: Register },

    // Organization с вложенными маршрутами
    {
      path: '/organization',
      component: OrganizationLayout,
      redirect: '/organization/main',
      children: [
        { path: 'main', component: OrgMain },
        { path: 'structure', component: OrgStructure },
        { path: 'docs', component: OrgDocs },
        { path: 'education', component: OrgEducation },
        { path: 'management', component: OrgManagement },
        { path: 'staff', component: OrgStaff },
        { path: 'facilities', component: OrgFacilities },
        { path: 'services', component: OrgServices },
        { path: 'finance', component: OrgFinance },
        { path: 'vacancies', component: OrgVacancies },
        { path: 'international', component: OrgInternational },
      ],
    },

    // Clients с вложенными маршрутами
    {
      path: '/clients',
      component: ClientsLayout,
      redirect: '/clients/important',
      children: [
        { path: 'important', component: ClientsImportant },
        { path: 'holidays', component: ClientsHolidays },
        { path: 'payment', component: ClientsPayment },
        { path: 'tax', component: ClientsTax },
      ],
    },

    {
      path: '/account',
      component: AccountLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', component: Profile },
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
