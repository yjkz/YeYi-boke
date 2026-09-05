import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
// 字体分片 @font-face（npm run font:build 生成）；用 Vite 惯用的显式 import 而非
// style.css @import，避免与 @tailwind 指令的 @import 顺序约束
import './font-split.css'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
