# ============================================================
# Etapa 1: Compilación de la aplicación Angular 22
# ============================================================
FROM node:20-alpine AS build

WORKDIR /app

# Instalar dependencias con caché de capas
COPY package*.json ./
RUN npm install

# Copiar código fuente y compilar
COPY . .
RUN npm run build

# ============================================================
# Etapa 2: Servidor Web Nginx de Producción
# ============================================================
FROM nginx:alpine

# Configuración Nginx optimizada para SPA y proxy inverso
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar artefactos compilados desde la etapa de build
COPY --from=build /app/dist/casillas-frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
