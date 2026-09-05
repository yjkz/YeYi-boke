FROM node:24-slim AS builder
# 注：builder 弃用 node:24-alpine —— cn-font-split 的原生内核在 musl 下不可用
# （isMusl 回退到 wasm，但 koffi FFI 只认 ELF 共享库），详见 task-2-report。
WORKDIR /frontend
COPY ./package.json .
COPY ./package-lock.json .
RUN npm ci
# cn-font-split 原生子集化内核：npm install-scripts 允许列表可能拦截其 postinstall，
# 且 slim 镜像没有 curl，故用 Node 内置 fetch 显式下载 glibc 版共享库
# （内核版本 7.6.8 与 cn-font-split@7.4.3 官方 init 脚本所取 latest 一致）
RUN node -e "const fs=require('fs');const url='https://github.com/KonghaYao/cn-font-split/releases/download/7.6.8/libffi-x86_64-unknown-linux-gnu.so';fetch(url).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.arrayBuffer()}).then(b=>{fs.writeFileSync('node_modules/cn-font-split/dist/libffi-x86_64-unknown-linux-gnu.so',Buffer.from(b));console.log('cn-font-split core downloaded',b.byteLength)})"
COPY . .
RUN npm run font:build
RUN npm run build

FROM node:24-alpine as runner
WORKDIR /frontend
COPY --from=builder /frontend/.output ./.output
CMD ["node", ".output/server/index.mjs"]
