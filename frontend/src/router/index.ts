import { createRouter, createWebHistory } from 'vue-router'
import { checkAuth, checkRole, checkStaff, checkAdmin, redirectAuthenticated } from './guards'

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

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/courses',
      name: 'courses',
      component: Courses
    },
    {
      path: '/enroll',
      name: 'enroll',
      component: Enroll
    },
    {
      path: '/testing',
      name: 'testing',
      component: Testing
    },
    {
      path: '/jobs',
      name: 'jobs',
      component: Jobs
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: Privacy
    },
    {
      path: '/consent',
      name: 'consent',
      component: Consent
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      beforeEnter: redirectAuthenticated
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
      beforeEnter: redirectAuthenticated
    },
    {
      path: '/organization',
      component: OrganizationLayout,
      children: [
        {
          path: '',
          name: 'organization',
          component: OrgMain
        },
        {
          path: 'structure',
          name: 'org-structure',
          component: OrgStructure
        },
        {
          path: 'docs',
          name: 'org-docs',
          component: OrgDocs
        },
        {
          path: 'education',
          name: 'org-education',
          component: OrgEducation
        },
        {
          path: 'management',
          name: 'org-management',
          component: OrgManagement
        },
        {
          path: 'staff',
          name: 'org-staff',
          component: OrgStaff
        },
        {
          path: 'facilities',
          name: 'org-facilities',
          component: OrgFacilities
        },
        {
          path: 'services',
          name: 'org-services',
          component: OrgServices
        },
        {
          path: 'finance',
          name: 'org-finance',
          component: OrgFinance
        },
        {
          path: 'vacancies',
          name: 'org-vacancies',
          component: OrgVacancies
        },
        {
          path: 'grants',
          name: 'org-grants',
          component: OrgGrants
        },
        {
          path: 'accessibility',
          name: 'org-accessibility',
          component: OrgAccessibility
        },
        {
          path: 'international',
          name: 'org-international',
          component: OrgInternational
        }
      ]
    },
    {
      path: '/clients',
      component: ClientsLayout,
      meta: { requiresAuth: true, allowedRoles: ['admin', 'staff', 'student'] },
      beforeEnter: checkRole(['admin', 'staff', 'student']),
      children: [
        {
          path: 'holidays',
          name: 'clients-holidays',
          component: ClientsHolidays
        },
        {
          path: 'payment',
          name: 'clients-payment',
          component: ClientsPayment
        },
        {
          path: 'tax',
          name: 'clients-tax',
          component: ClientsTax
        }
      ]
    },
    {
      path: '/account',
      component: AccountLayout,
      meta: { requiresAuth: true },
      beforeEnter: checkAuth,
      children: [
        {
          path: '',
          name: 'account',
          component: AccountDashboard
        },
        {
          path: 'forms',
          name: 'account-forms',
          component: AccountForms,
          meta: { requiresStaff: true },
          beforeEnter: checkStaff
        },
        {
          path: 'documents',
          name: 'account-documents',
          component: AccountDocuments
        }
      ]
    }
  ]
})

export default router
