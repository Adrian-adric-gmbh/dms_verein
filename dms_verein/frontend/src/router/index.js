import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory('/verein'),
  routes: [
    // Öffentliche Seiten — scrollen via PublicLayout
    {
      path: '/',
      component: () => import('@/views/public/PublicLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/views/public/HomeView.vue') },
        { path: 'antrag', name: 'antrag', component: () => import('@/views/public/AntragView.vue') },
        { path: 'kalender', name: 'kalender', component: () => import('@/views/public/KalenderView.vue') },
        { path: 'login', name: 'login', component: () => import('@/views/public/LoginView.vue') },
        { path: 'impressum', name: 'impressum', component: () => import('@/views/public/ImpressumView.vue') },
        { path: 'datenschutz', name: 'datenschutz', component: () => import('@/views/public/DatenschutzView.vue') },
        { path: 'sparte/:name', name: 'sparte-detail', component: () => import('@/views/public/SparteDetailView.vue') },
        { path: 'blog', name: 'blog', component: () => import('@/views/public/BlogView.vue') },
        { path: 'produkt', name: 'produkt', component: () => import('@/views/public/ProduktView.vue') },
        { path: 'blog/:slug', name: 'blog-post', component: () => import('@/views/public/BlogPostView.vue') },
      ],
    },

    // Mitglieder-Portal
    {
      path: '/portal',
      component: () => import('@/views/portal/PortalLayout.vue'),
      meta: { requiresAuth: true, requiresRole: 'Mitglied' },
      children: [
        { path: '', name: 'portal-home', component: () => import('@/views/portal/PortalHome.vue') },
        { path: 'profil', name: 'portal-profil', component: () => import('@/views/portal/PortalProfil.vue') },
        { path: 'beitraege', name: 'portal-beitraege', component: () => import('@/views/portal/PortalBeitraege.vue') },
        { path: 'kalender', name: 'portal-kalender', component: () => import('@/views/portal/PortalKalender.vue') },
        { path: 'alben', name: 'portal-alben', component: () => import('@/views/portal/PortalAlben.vue') },
        { path: 'abstimmungen', name: 'portal-abstimmungen', component: () => import('@/views/portal/PortalAbstimmungen.vue') },
        { path: 'sparten/:name', name: 'portal-sparte', component: () => import('@/views/portal/PortalSparte.vue') },
        { path: 'blog', name: 'portal-blog', component: () => import('@/views/portal/PortalBlogView.vue') },
        { path: 'blog/:name/baukasten', name: 'portal-blog-builder', component: () => import('@/views/portal/PortalBlogBuilderView.vue') },
        { path: 'chat', name: 'portal-chat', component: () => import('@/views/portal/PortalChatView.vue') },
      ],
    },

    // Admin-Bereich
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        { path: '', name: 'admin-dashboard', component: () => import('@/views/admin/DashboardView.vue') },
        { path: 'mitglieder', name: 'admin-mitglieder', component: () => import('@/views/admin/MitgliederView.vue') },
        { path: 'mitglieder/:id', name: 'admin-mitglied-detail', component: () => import('@/views/admin/MitgliedDetailView.vue') },
        { path: 'antraege', name: 'admin-antraege', component: () => import('@/views/admin/AntraegeView.vue') },
        { path: 'sparten', name: 'admin-sparten', component: () => import('@/views/admin/SpartenView.vue') },
        { path: 'sparten/:name/baukasten', name: 'admin-sparten-builder', component: () => import('@/views/admin/SpartenBuilderView.vue') },
        { path: 'blog', name: 'admin-blog', component: () => import('@/views/admin/BlogAdminView.vue') },
        { path: 'blog/:name/baukasten', name: 'admin-blog-builder', component: () => import('@/views/admin/BlogBuilderView.vue') },
        { path: 'veranstaltungen', name: 'admin-events', component: () => import('@/views/admin/EventsView.vue') },
        { path: 'fotoalben', name: 'admin-alben', component: () => import('@/views/admin/AlbenView.vue') },
        { path: 'vorstand', name: 'admin-vorstand', component: () => import('@/views/admin/VorstandView.vue') },
        { path: 'finanzen', name: 'admin-finanzen', component: () => import('@/views/admin/FinanzenView.vue') },
        { path: 'rechnungen', name: 'admin-rechnungen', component: () => import('@/views/admin/RechnungenView.vue') },
        { path: 'sepa', name: 'admin-sepa', component: () => import('@/views/admin/SepaView.vue') },
        { path: 'beitragsklassen', name: 'admin-beitragsklassen', component: () => import('@/views/admin/BeitragsklassenView.vue') },
        { path: 'mailing', name: 'admin-mailing', component: () => import('@/views/admin/MailingView.vue') },
        { path: 'protokolle', name: 'admin-protokolle', component: () => import('@/views/admin/ProtokolleView.vue') },
        { path: 'abstimmungen', name: 'admin-abstimmungen', component: () => import('@/views/admin/AbstimmungenView.vue') },
        { path: 'konfiguration', name: 'admin-config', component: () => import('@/views/admin/KonfigurationView.vue') },
      ],
    },

    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user) await auth.init()

  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !auth.canAccessAdmin) {
    return { name: 'home' }
  }
  // Adminbereich nur auf Desktop (≥1024px) — auf Handy/Tablet immer Portal
  if (to.path.startsWith('/admin') && auth.isMitglied && window.innerWidth < 1024) {
    return { name: 'portal-home' }
  }
})

export default router
