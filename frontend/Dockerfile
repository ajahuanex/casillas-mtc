FROM nginx:alpine

# Copiar configuración de Nginx optimizada para SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar aplicación Angular compilada
COPY dist/casillas-frontend/browser /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
