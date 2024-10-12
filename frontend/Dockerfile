# Fáze 1: Sestavení React aplikace
FROM node:16 AS build

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování package.json a package-lock.json
COPY package*.json ./

# Instalace závislostí
RUN npm install

# Kopírování všech ostatních souborů
COPY . .

# Sestavení aplikace pro produkci
RUN npm run build

# Fáze 2: Nasazení sestavené aplikace pomocí http-server
FROM node:16-alpine

# Instalace http-server
RUN npm install -g http-server

# Nastavení pracovního adresáře
WORKDIR /app

# Kopírování sestavených souborů z předchozí fáze
COPY --from=build /app/build /app/build

# Exponování portu 3000
EXPOSE 3007

# Spuštění aplikace pomocí http-server
CMD ["http-server", "build", "-p", "3007"]
