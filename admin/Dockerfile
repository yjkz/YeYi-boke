FROM node:24-slim AS builder
# 注：builder 弃用 node:24-alpine —— cn-font-split 的原生内核在 musl 下不可用
# （isMusl 回退到 wasm，但 koffi FFI 只认 ELF 共享库），详见 task-2-report。
WORKDIR /admin
COPY ./package*.json ./
RUN npm ci
# cn-font-split 原生子集化内核：npm install-scripts 允许列表可能拦截其 postinstall，
# 且 slim 镜像没有 curl，故用 Node 内置 fetch 显式下载 glibc 版共享库
# （内核版本 7.6.8 与 cn-font-split@7.4.3 官方 init 脚本所取 latest 一致）。
# 内核会被 dlopen 执行，必须校验 sha256，防上游 release 资产被替换成恶意代码
RUN node -e "const fs=require('fs'),crypto=require('crypto');const url='https://github.com/KonghaYao/cn-font-split/releases/download/7.6.8/libffi-x86_64-unknown-linux-gnu.so';const expect='db4690e3b9c4b04f6dfa5965792585c389914038f6a4c90fbe73baaf16bbf19c';fetch(url).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.arrayBuffer()}).then(b=>{const actual=crypto.createHash('sha256').update(Buffer.from(b)).digest('hex');if(actual!==expect){console.error('cn-font-split core sha256 mismatch: expected '+expect+' got '+actual);process.exit(1)}fs.writeFileSync('node_modules/cn-font-split/dist/libffi-x86_64-unknown-linux-gnu.so',Buffer.from(b));console.log('cn-font-split core downloaded and sha256-verified',b.byteLength,'bytes')})"
COPY . .
ARG VITE_BLOG_URL=http://localhost:3000
ENV VITE_BLOG_URL=$VITE_BLOG_URL
RUN npm run font:build
RUN npm run build

FROM nginx:alpine AS runner
COPY --from=builder /admin/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
