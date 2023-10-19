# Angular Development Dockerfile

FROM node:16.14

# Create app directory
WORKDIR /app

# Install app dependencies
COPY package.json ./

#check if video.js is inside the copied packacge.json if not break the build
RUN if grep -q "video.js" package.json; then echo "video.js found"; else echo "video.js not found"; exit 1; fi
RUN cat package.json
RUN npm install --timeout=300000

# Exclude unnecessary files
COPY . .

EXPOSE 4200
ENTRYPOINT ["npm", "run"]
CMD ["docker-serve"]