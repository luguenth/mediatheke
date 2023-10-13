# Mediatheke

## Overview 🌐

Mediatheke is an online viewer, still in its alpha phase, that taps into the "Filmliste" from [MediathekView Project](https://mediathekview.de/). The goal is simple: make it easier to search and stream movies and series from German public TV. If you're interested in the project and want to help, feel free to jump in. All contributions are appreciated.

### Features 📋

- [x] **Search Functionality**: Quickly locate movies and series from German public TV.
  
- [x] **Online Viewer**: Stream content directly.
  
- [x] **Background Jobs**: "Filmliste" updates happen automatically to keep the library fresh.
  
- [x] **User Authentication**: Extra security measures for both content and user settings.
  
- [x] **Recommendations**: Suggest and share favorites with others.
  
- [x] **Similar Content**: Find similar Videos to what you're watching.

- [ ] **User Preferences**: In the works—soon you'll be able to save your go-to movies and series to a personal watchlist.
  
- [ ] **Registration**: Also in the works—registration coming soon. Currently, it's by invitation only.

### Known Issues 🐛

- [ ] Search bar acts up if you leave the start page.
  
- [ ] Some content can't be played due to unsupported formats.
  
- [ ] Some content isn't imported yet, still figuring out why.

- [ ] Videos which are not in landscape format are not displayed correctly.

#### Development Issues

- [ ] Server cant find Database Container on first start, restart fixes it.

Remember, this project is in its alpha stage, so expect some quirks. Contributions to fix these are more than welcome.

## How to Get Started 🛠️

### What You'll Need 📦

- Docker
- Docker Compose
- mkcert

### Setup Steps 📝

1. Set Up Your Environment
```
cp .env.example .env
```
2. Make necessary changes to .env file as needed

3. Fire Up the Containers
```
docker-compose up -d
```

4. Trust the Certificates
```
mkcert -install
mkcert -cert-file Configuration/certs/mediatheke.local.pem -key-file Configuration/certs/mediatheke.local-key.pem mediatheke.local
```
5. Open `https://mediatheke.local` in your web browser.

### Container Roles 🔍

| Container  | What It Does             |
|------------|--------------------------|
| database   | Holds the data in Postgres|
| redis      | Manages Celery tasks and caching|
| server     | Handles the backend with FastAPI|
| client     | Manages the frontend via Angular|
| nginx      | Merges everything under one port with a reverse proxy|
| typesense  | Takes care of search|

## Want to Contribute? 🤝

The project is in its early stages and could use some extra hands. If you're interested in contributing, feel free to reach out. All contributions are welcome.
