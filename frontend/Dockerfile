# Vytvoření základního obrazu
FROM node:16 AS build

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování souborů
COPY package*.json ./
RUN npm install

COPY . .

# Sestavení aplikace
RUN npm run build

# Vytvoření produkčního obrazu
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Exponování portu
EXPOSE 80
