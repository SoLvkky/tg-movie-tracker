# CHANGELOG

## [1.0.2] - 2026-01-20

### Added

- Full Multi-language support (5 languages)
- I18n Middleware & Handler

### Changed

- In the English localization, "Series" has been renamed to "TV Series"
- API functions have been merged
- Content handler functions have been merged
- CRUD operations are grouped by tables
- The number of results has been normalized across all functions

## [1.0.1] - 2026-01-18

### Added

- "Trending" section: A list of movies and TV series that are trending this week
- API has been added for the future Mini App.

### Fixed

- Case of double logging in TMDB_API
- Сase where the BACK button was not working correctly on the movies and TV series page.

## [1.0.0] - 2026-01-16

### Added

- Searching/adding TV series
- Bot start code

### Changed

- The database structure, models and dependencies
- Content handlers
- Main Menu appearance
- Search states

### Fixed

- Сase where pressing the "Back" button in the similar movies menu did not return to the movie itself
- All migrations are placed in a single file

## [1.0.0-beta.2] - 2026-01-08

### Added

- Adult Mode (Customizable access to adult films)
- Settings menu

### Changed

- Docker functions in Docker instruction merged into a single one
- "Back" button was placed in a separate file
- All menu functions were moved to a separate file
- The function for retrieving the release year has been redesigned to avoid bugs
- The callback data was grouped by callback type
- Functions for retrieving and switching the adult mode within the database
- Checking the DB status in Docker-compose.yml

### Fixed

- Case, where movies were not added to the watched library.
- Case, in which the movie pages from the viewed films library did not open.
- Case, where the search for similar movies was not working
- Docker did not perform the database migration
- In some cases, the bot did not respond to button presses
- Incorrect display of buttons

## [1.0.0-beta.1] - 2026-01-04

### Added

- Public release of the movie tracker bot on GitHub
- Main functionality: adding/viewing movies, statistics
