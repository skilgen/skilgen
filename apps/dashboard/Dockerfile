FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json turbo.json ./
COPY apps/dashboard/package*.json ./apps/dashboard/
COPY packages/ ./packages/

RUN npm ci

COPY apps/dashboard/ ./apps/dashboard/

RUN npm run build --workspace=skillayer-dashboard

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/apps/dashboard/.next/standalone ./
COPY --from=builder /app/apps/dashboard/.next/static ./apps/dashboard/.next/static
COPY --from=builder /app/apps/dashboard/public ./apps/dashboard/public

EXPOSE 3000

CMD ["node", "apps/dashboard/server.js"]
