FROM node:24-alpine AS builder
WORKDIR /admin
COPY ./package*.json ./
RUN npm ci
COPY . .
ARG VITE_BLOG_URL=http://localhost:3000
ENV VITE_BLOG_URL=$VITE_BLOG_URL
RUN npm run build

FROM nginx:alpine AS runner
COPY --from=builder /admin/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
CMD ["nginx", "-g", "daemon off;"]
