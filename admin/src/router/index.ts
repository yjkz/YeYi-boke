import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
        { path: 'posts', name: 'PostList', component: () => import('@/views/PostList.vue') },
        { path: 'posts/new', name: 'PostNew', component: () => import('@/views/PostEdit.vue') },
        {
          path: 'posts/:id/edit',
          name: 'PostEdit',
          component: () => import('@/views/PostEdit.vue'),
        },
        {
          path: 'comments',
          name: 'CommentList',
          component: () => import('@/views/CommentList.vue'),
        },
        {
          path: 'categories',
          name: 'CategoryList',
          component: () => import('@/views/CategoryList.vue'),
        },
        { path: 'tags', name: 'TagList', component: () => import('@/views/TagList.vue') },
        {
          path: 'settings',
          name: 'SiteConfig',
          component: () => import('@/views/SiteConfig.vue'),
        },
        { path: 'analytics', name: 'Analytics', component: () => import('@/views/Analytics.vue') },
        { path: 'password', name: 'ChangePassword', component: () => import('@/views/ChangePassword.vue') },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) {
    return '/login'
  }
  if (auth.token && !auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      auth.logout()
      return '/login'
    }
  }
})

export default router
