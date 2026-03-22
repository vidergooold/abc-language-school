import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/pages/Home.vue'
import Courses from '@/pages/Courses.vue'
import Login from '@/pages/Login.vue'
import Register from '@/pages/Register.vue'
import Enroll from '@/pages/Enroll.vue'
import Testing from '@/pages/Testing.vue'
import Jobs from '@/pages/Jobs.vue'
import Privacy from '@/pages/Privacy.vue'
import Consent from '@/pages/Consent.vue'

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
import OrgGrants from '@/pages/organization/Grants.vue'
import OrgAccessibility from '@/pages/organization/Accessibility.vue'
import OrgInternational from '@/pages/organization/International.vue'

import ClientsLayout from '@/components/layout/ClientsLayout.vue'
import ClientsHolidays from '@/pages/clients/Holidays.vue'
import ClientsPayment from '@/pages/clients/Payment.vue'
import ClientsTax from '@/pages/clients/Tax.vue'

import AccountLayout from '@/components/layout/AccountLayout.vue'
import AccountDashboard from '@/pages/account/Dashboard.vue'
import AccountForms from '@/pages/account/Forms.vue'
import AccountDocuments from '@/pages/account/Documents.vue'
import AccountStudents from '@/pages/account/Students.vue'
import AccountNews from '@/pages/account/News.vue'
import AccountScheduleAdmin from '@/pages/account/ScheduleAdmin.vue'
import AccountFeedback from '@/pages/account/Feedback.vue'

import AnketaShkolnik from '@/pages/blanks/AnketaShkolnik.vue'
import AnketaVzrosly from '@/pages/blanks/AnketaVzrosly.vue'
import AnketaDoshkolnik from '@/pages/blanks/AnketaDoshkolnik.vue'

import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' }
  },
  routes: [
    { path: '/', component: Home },
    { path: '/courses', component: Courses },
    { path: '/enroll', component: Enroll },
    { path: '/testing', component: Testing },
    { path: '/jobs', component: Jobs },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/privacy', component: Privacy },
    { path: '/consent', component: Consent },
    { path: '/blanks/shkolnik', component: AnketaShkolnik, meta: { requiresStaff: true } },
    { path: '/blanks/vzrosly', component: AnketaVzrosly, meta: { requiresStaff: true } },
    { path: '/blanks/doshkolnik', component: AnketaDoshkolnik, meta: { requiresStaff: true } },
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
        { path: 'grants', component: OrgGrants },
        { path: 'accessibility', component: OrgAccessibility },
        { path: 'international', component: OrgInternational },
      ],
    },
    {
      path: '/clients',
      component: ClientsLayout,
      redirect: '/clients/holidays',
      children: [
        { path: 'holidays', component: ClientsHolidays },
        { path: 'payment', component: ClientsPayment },
        { path: 'tax', component: ClientsTax },
      ],
    },
    {
      path: '/account',
      component: AccountLayout,
      meta: { requiresStaff: true },
      redirect: '/account/dashboard',
      children: [
        { path: 'dashboard', component: AccountDashboard },
        { path: 'forms', component: AccountForms },
        { path: 'documents', component: AccountDocuments },
        { path: 'students', component: AccountStudents },
        { path: 'news', component: AccountNews, meta: { requiresAdmin: true } },
        { path: 'schedule', component: AccountScheduleAdmin },
        { path: 'feedback', component: AccountFeedback },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresStaff && !auth.isStaff) {
    return '/login'
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return '/account/dashboard'
  }
})

export default router
