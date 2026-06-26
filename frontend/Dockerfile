FROM node:20-alpine AS builder
WORKDIR /frontend
COPY ./package.json .
COPY ./package-lock.json .
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine as runner
WORKDIR /frontend
COPY --from=builder /frontend/.output ./.output
CMD ["node", ".output/server/index.mjs"]
