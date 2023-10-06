# Angular Development Dockerfile

# Angular Development Dockerfile

FROM node:16.14

# Create app directory
WORKDIR /app

# Install app dependencies
COPY package*.json ./
RUN npm install

# Exclude unnecessary files
COPY . .

EXPOSE 4200
ENTRYPOINT ["npm", "run"]
CMD ["docker-serve"]