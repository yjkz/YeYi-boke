export default defineNuxtConfig({
  devtools: { enabled: true },

  // SSR enabled by default in Nuxt 3, explicit for clarity
  ssr: true,

  modules: ['@nuxtjs/tailwindcss', '@nuxtjs/color-mode'],
  colorMode: {
    classSuffix: '',
    preference: 'light',
    fallback: 'light',
  },

  runtimeConfig: {
    apiBase: '',
    public: {
      apiBase: '/api/v1',
    },
  },

  app: {
    head: {
      title: 'YeYi 的博客',
      htmlAttrs: { lang: 'zh-CN' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '记录生活与代码' },
        { property: 'og:title', content: 'YeYi 的博客' },
        { property: 'og:description', content: '记录生活与代码' },
        { property: 'og:type', content: 'website' },
        { name: 'theme-color', content: '#FFF6E0' },
      ],
      link: [
        {
          rel: 'preload',
          href: '/fonts/AlimamaFangYuanTi.otf',
          as: 'font',
          type: 'font/otf',
          crossorigin: '',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],
  compatibilityDate: '2024-07-01',
})
