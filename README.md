# MovieTracker Bot

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-black?logo=github)

A Telegram bot that helps users build a personal movie collection, track genre-based stats, and discover similar films — all without leaving Telegram

The bot is designed to be fully interactive: almost all actions are performed via inline buttons, not text commands.

## Features

- Add movies to your personal collection
- View and manage what you’ve added
- Genre analytics – see your most-watched genres and distribution
- Similar movie suggestions based on your preferences
- Search for movies by title

## Tech Stack

- Python 3.12+
- Aiogram (async Telegram bot framework)
- PostgreSQL
- Alembic
- TMDB API (movie info)
- Docker (optional)

## Project Structure

```bash
project/
│
├── bot/
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── handlers/
│   ├── keyboards/
│   ├── middlewares/
│   └── states/
│
├── database/
│   ├── crud.py
│   ├── database.py
│   └── models.py
│
└── services/
    └── tmdb_api.py
```

## How It Works

1. User enters a movie name
2. Bot fetches metadata (local DB or TMDB)
3. User choose the desired movie
4. User confirms adding the movie
5. The movie goes into their personal collection
6. Stats update automatically

## Commands

```bash
/start - Bot initialization
/menu - Main menu
```

## Installation

### Using Docker Compose (recommended)

Make sure you have Docker and Docker Compose installed.

- Copy the repository

```bash
git clone https://github.com/SoLvkky/tg-movie-tracker
cd tg-movie-tracker/
```

- Insert the required environment variables

```bash
#.env
BOT_TOKEN # Your Telegram Bot Token
TMDB_APIKEY # Your TMDB API Autohrization key
DATABASE_URL # Async URL of your Database
DATABASE_SYNC_UR # Sync URL of your Database
```

Example variables are located in .env.example

- Build and start the stack:

```bash
docker-compose build
docker-compose up -d
```

### Using Python

- Copy and initialize the repository

```bash
git clone https://github.com/SoLvkky/tg-movie-tracker
cd tg-movie-tracker/
python -m venv .venv
pip install -r requirements.txt
```

- Insert the required environment variables

```bash
#.env
BOT_TOKEN # Your Telegram Bot Token
TMDB_APIKEY # Your TMDB API Autohrization key
DATABASE_URL # Async URL of your Database
DATABASE_SYNC_UR # Sync URL of your Database
```

- Start your bot

```bash
python -m bot.main
```
