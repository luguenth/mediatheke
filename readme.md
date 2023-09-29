# Mediatheke

## Overview

Mediatheke is an online viewer that taps into the "Filmliste" from the MediathekView Project (https://mediathekview.de/) to offer a streamlined way to search for and watch movies and series from German public TV stations. This project is still in development.


### Features

- [x] Search Functionality: Easily search for movies and series from German public TV stations.

- [x] Online Viewer: Offers the ability to watch selected movies and series online.

- [x] Background Jobs: Automatic updating of the "Filmliste" to keep the content up-to-date.

- [x] User Authentication: Secure user authentication system to protect content and user preferences.

- [x] Recommendations: Users can recommend movies and series to other users.

- [x] Similar Content: Users can discover similar content based on the Video they are currently watching.

- [ ] User Preferences: Ability to save movies and series to a personal watchlist.

- [ ] Registration: Users can register to the platform. (Currently only admins can invite users)


### Known Bugs

- [ ] The search bar only works on the start page. When navigating to another page, the search bar does not work anymore.

- [ ] Some Movies/Series are not playable. Because they have a currently not supported format.

- [ ] Some Movies/Series are not imported. This is still to be investigated.

## Development
### Requirements

- Docker
- Docker Compose

### Setup

1. Clone this repository `git clone --recursive https://github.com/codezeit/Mediatheke-Development.git`
2. Copy `.env.example` to `.env` and edit it to your needs
   ( right now we actually don't support any configuration directly in the
   `.env` file in this layer. But we'll add it in the future )
3. Run `docker-compose up -d` to start the containers or `docker-compose up` to
   start the containers and watch the logs
4. In the Browser go to https://localhost and accept the self-signed certificate

### Overview

The application is split into multiple containers:

| Container | Description | internal address | external address |
|-----------|-------------|------------------|------------------|
| [Client](https://github.com/codezeit/Mediatheke-Client) | The frontend of Mediatheke | http://client:4200 | http://localhost |
| [Server](https://github.com/codezeit/Mediatheke-Server) | The backend of Mediatheke | http://server:8000 | http://localhost/api |
| [Database](https://hub.docker.com/_/postgres) | The database of Mediatheke | postgres://postgres:postgres@database:5432/postgres | - |
| [nginx](https://hub.docker.com/_/nginx) | The reverse proxy for the frontend and backend | - | http://localhost |

## Contributing

You can contribute to this project by opening an issue or by creating a pull request.