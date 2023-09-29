import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/news/' },
  {
    name: 'news',
    path: '/news/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('src/pages/NewsPage.vue') }],
    meta: { requiresAuth: false }
  },

  {
    name: 'annotation_tasks',
    path: '/annotation_tasks/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('src/pages/TaskPage.vue') }],
    meta: { requiresAuth: true }
  },
  {
    name: 'annotation_statistics',
    path: '/annotation_statistics/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('src/pages/UsersPage.vue') }],
    meta: { requiresAuth: true }
  },

  {
    name: 'users',
    path: '/users/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('src/pages/UsersPage.vue') }],
    meta: { requiresAuth: true }
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('src/pages/ErrorNotFound.vue')
  }
]

export default routes
