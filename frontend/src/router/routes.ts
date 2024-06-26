import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/news/' },
  {
    name: 'news',
    path: '/news/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('src/pages/NewsPage.vue') }],
    meta: { requiresAuth: false },
  },

  {
    name: 'annotation_tasks',
    path: '/annotation_tasks/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('src/pages/TaskPage.vue') }],
    meta: { requiresAuth: true },
  },
  {
    name: 'annotate_task',
    path: '/annotation_tasks/:task_id',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('src/pages/AnnotationPage.vue') },
    ],
    meta: { requiresAuth: true },
  },
  {
    name: 'annotation_results',
    path: '/annotation_results/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('src/pages/ResultsPage.vue') },
    ],
    meta: { requiresAuth: true },
  },
  {
    name: 'time_tracking',
    path: '/time_tracking/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('src/pages/TimeTrackingPage.vue') },
    ],
    meta: { requiresAuth: true },
  },
  {
    name: 'annotation_statistics',
    path: '/annotation_statistics/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('src/pages/StatisticsPage.vue') },
    ],
    meta: { requiresAuth: true },
  },

  {
    name: 'users',
    path: '/users/',
    component: () => import('src/layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('src/pages/UsersPage.vue') },
    ],
    meta: { requiresAuth: true },
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('src/pages/ErrorNotFound.vue'),
  },
];

export default routes;
