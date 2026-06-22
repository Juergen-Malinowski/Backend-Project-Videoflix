# Videoflix Backend

Videoflix Backend is a Django REST Framework backend for a Netflix-inspired video platform.

The backend uses a Docker-based setup with PostgreSQL, Redis, RQ, WhiteNoise and Gunicorn.

## Setup

Run the following commands to set up the project locally.

```bash
# Clone repository
git clone https://github.com/Juergen-Malinowski/Backend-Project-Videoflix.git

# Open backend folder
cd Backend-Project-Videoflix

# Create local environment file
cp .env.template .env

# Build and start Docker containers
docker-compose up --build
```

If `docker-compose` is not available, use the newer Docker Compose syntax:

```bash
docker compose up --build
```

Open the Django admin in the browser:

```text
http://localhost:8000/admin/
```

The Docker entrypoint creates a superuser automatically from the following environment variables:

```text
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_PASSWORD
DJANGO_SUPERUSER_EMAIL
```

## Docker Setup Notes

This project uses the provided Videoflix Docker setup.

Important notes:

* Do not change `backend.Dockerfile`
* Do not change `docker-compose.yml`
* Do not change `backend.entrypoint.sh`
* Keep existing `.env.template` variable names unchanged
* Add new environment variables only when they are required
* Update `requirements.txt` whenever Python dependencies change
* Run database migrations inside the Docker container when the database schema changes

## Environment Variables

Environment variables are loaded from `.env`.

The `.env` file is created from `.env.template` and must not be committed.

Important variables:

| Name                        | Purpose                                         |
| --------------------------- | ----------------------------------------------- |
| `DJANGO_SUPERUSER_USERNAME` | Admin username created by the Docker entrypoint |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password created by the Docker entrypoint |
| `DJANGO_SUPERUSER_EMAIL`    | Admin email created by the Docker entrypoint    |
| `SECRET_KEY`                | Django secret key                               |
| `DEBUG`                     | Django debug mode                               |
| `ALLOWED_HOSTS`             | Allowed backend hosts                           |
| `CSRF_TRUSTED_ORIGINS`      | Trusted frontend origins                        |
| `DB_NAME`                   | PostgreSQL database name                        |
| `DB_USER`                   | PostgreSQL database user                        |
| `DB_PASSWORD`               | PostgreSQL database password                    |
| `DB_HOST`                   | PostgreSQL database host                        |
| `DB_PORT`                   | PostgreSQL database port                        |
| `REDIS_LOCATION`            | Redis cache location                            |
| `REDIS_HOST`                | Redis host                                      |
| `REDIS_PORT`                | Redis port                                      |
| `REDIS_DB`                  | Redis database index                            |
| `EMAIL_HOST`                | SMTP host                                       |
| `EMAIL_PORT`                | SMTP port                                       |
| `EMAIL_HOST_USER`           | SMTP user                                       |
| `EMAIL_HOST_PASSWORD`       | SMTP password                                   |
| `DEFAULT_FROM_EMAIL`        | Default sender address                          |

## Project Structure

```text
project_videoflix/
├── backend/
│   ├── core/
│   ├── .dockerignore
│   ├── .env.template
│   ├── .gitignore
│   ├── backend.Dockerfile
│   ├── backend.entrypoint.sh
│   ├── docker-compose.yml
│   ├── manage.py
│   ├── requirements.txt
│   └── README.md
└── frontend/
```

The frontend and backend are separated projects.

## Database Models

No project-specific database models have been implemented yet.

Currently available database structures come from:

* Django admin
* Django auth
* Django sessions
* django-rq
* SimpleJWT token blacklist

## Django Admin

The Django admin is available and currently includes:

* Django users
* Django groups
* Django RQ
* JWT token blacklist data

A default superuser is created automatically through the Docker entrypoint when the container starts.

## API Endpoints

No project-specific API endpoints have been implemented yet.

Planned endpoint areas will be added after the Videoflix API documentation has been analyzed.

## Testing

Automated tests have not been added yet.

Planned testing setup:

* pytest
* pytest-django
* endpoint-based test files
* app-based test folders
* mocked external services where needed

## Running Tests

No test suite is available yet.

The future test command will be:

```bash
python -m pytest
```

## Docker Commands

Start the project:

```bash
docker-compose up
```

Build and start the project:

```bash
docker-compose up --build
```

Alternative Docker Compose syntax:

```bash
docker compose up
```

```bash
docker compose up --build
```

Create migration files inside the Docker container:

```bash
docker-compose exec web python manage.py makemigrations
```

Apply migrations inside the Docker container:

```bash
docker-compose exec web python manage.py migrate
```

## Current Implementation Status

The backend project currently includes the Docker-based Django foundation.

Implemented so far:

* Docker setup files added
* Django project `core` created
* environment-based settings configured
* PostgreSQL configured through Docker
* Redis configured through Docker
* RQ configured through Docker
* WhiteNoise configured for static files
* media and static file settings added
* Django admin available
* automatic superuser creation through Docker entrypoint verified
* initial dependencies installed
* `requirements.txt` created
* first Docker build completed successfully
* PostgreSQL container started successfully
* Redis container started successfully
* backend container started successfully
* initial Django migrations applied successfully
* Django admin login verified
