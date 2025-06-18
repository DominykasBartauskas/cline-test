# TMDB API Backend

A FastAPI backend that ingests information from the TMDB API (movies, TV shows, anime) and stores it in a PostgreSQL database.

## Features

- Fetch and store data from TMDB API
- RESTful API for movies, TV shows, and anime
- User authentication and authorization
- User watchlists and ratings
- Search functionality
- Async database operations

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Relational database
- **Logfire**: Structured logging
- **UV**: Fast Python package installer and resolver
- **Pre-commit**: Git hooks for code quality (black, isort, pyright)

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- TMDB API key (get one from [themoviedb.org](https://www.themoviedb.org/documentation/api))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tmdb-api-backend.git
cd tmdb-api-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies using UV:

```bash
pip install uv
uv pip install -r requirements.txt
```

4. Set up environment variables:

Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
```

Update the following values in the `.env` file:
- `SECRET_KEY`: Your secret key for JWT tokens
- `TMDB_API_KEY`: Your TMDB API key
- Database connection details

5. Set up the database:

```bash
alembic upgrade head
```

6. Install pre-commit hooks:

```bash
pre-commit install
```

### Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

API documentation will be available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Initial Data Setup

To populate the database with initial data from TMDB:

```bash
# Sync genres
curl -X POST http://localhost:8000/api/sync/genres

# Sync popular movies
curl -X POST http://localhost:8000/api/sync/movies/popular

# Sync popular TV shows
curl -X POST http://localhost:8000/api/sync/tv/popular
```

## API Endpoints

### Movies

- `GET /api/movies`: List movies
- `GET /api/movies/{id}`: Get movie details
- `GET /api/movies/popular`: Get popular movies
- `GET /api/movies/top_rated`: Get top-rated movies

### TV Shows

- `GET /api/tv`: List TV shows
- `GET /api/tv/{id}`: Get TV show details
- `GET /api/tv/popular`: Get popular TV shows
- `GET /api/tv/top_rated`: Get top-rated TV shows

### Genres

- `GET /api/genres`: List all genres
- `GET /api/genres/movies`: List movie genres
- `GET /api/genres/tv`: List TV show genres

### Search

- `GET /api/search/multi`: Search for movies and TV shows
- `GET /api/search/movies`: Search for movies
- `GET /api/search/tv`: Search for TV shows

### Users

- `POST /api/users/token`: Get access token
- `GET /api/users/me`: Get current user
- `GET /api/users/me/watchlist`: Get current user's watchlist
- `POST /api/users/me/watchlist/movies/{movie_id}`: Add movie to watchlist
- `DELETE /api/users/me/watchlist/movies/{movie_id}`: Remove movie from watchlist
- `POST /api/users/me/watchlist/tv/{tv_show_id}`: Add TV show to watchlist
- `DELETE /api/users/me/watchlist/tv/{tv_show_id}`: Remove TV show from watchlist
- `GET /api/users/me/ratings/movies`: Get user's movie ratings
- `POST /api/users/me/ratings/movies`: Create movie rating
- `PUT /api/users/me/ratings/movies/{movie_id}`: Update movie rating
- `DELETE /api/users/me/ratings/movies/{movie_id}`: Delete movie rating
- `GET /api/users/me/ratings/tv`: Get user's TV show ratings
- `POST /api/users/me/ratings/tv`: Create TV show rating
- `PUT /api/users/me/ratings/tv/{tv_show_id}`: Update TV show rating
- `DELETE /api/users/me/ratings/tv/{tv_show_id}`: Delete TV show rating

### Sync

- `POST /api/sync/genres`: Sync genres from TMDB
- `POST /api/sync/movies/popular`: Sync popular movies from TMDB
- `POST /api/sync/tv/popular`: Sync popular TV shows from TMDB
- `POST /api/sync/movies/{tmdb_id}`: Sync specific movie from TMDB
- `POST /api/sync/tv/{tmdb_id}`: Sync specific TV show from TMDB

## Development

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- pyright for type checking

These tools are configured in `pyproject.toml` and run automatically via pre-commit hooks.

### Database Migrations

To create a new migration after model changes:

```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
