FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Копируем уже собранный dist с хоста
COPY dist ./

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
