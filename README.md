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

## Table of Contents

* [Docker Setup Notes](#docker-setup-notes)
* [Environment Variables](#environment-variables)
* [Project Structure](#project-structure)
* [Database Models](#database-models)
  * [`videos_app.Video`](#videos_appvideo)
* [Django Admin](#django-admin)
* [API Endpoints](#api-endpoints)
  * [Authentication Endpoints](#authentication-endpoints)
  * [Video Endpoints](#video-endpoints)
* [Authentication](#authentication)
* [Testing](#testing)
* [Running Tests](#running-tests)
* [Docker Commands](#docker-commands)
* [Current Implementation Status](#current-implementation-status)

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

| Name                        | Purpose                                               |
| --------------------------- | ----------------------------------------------------- |
| `DJANGO_SUPERUSER_USERNAME` | Admin username created by the Docker entrypoint       |
| `DJANGO_SUPERUSER_PASSWORD` | Admin password created by the Docker entrypoint       |
| `DJANGO_SUPERUSER_EMAIL`    | Admin email created by the Docker entrypoint          |
| `SECRET_KEY`                | Django secret key                                     |
| `DEBUG`                     | Django debug mode                                     |
| `ALLOWED_HOSTS`             | Allowed backend hosts                                 |
| `CSRF_TRUSTED_ORIGINS`      | Trusted frontend origins                              |
| `FRONTEND_BASE_URL`         | Frontend base URL used for email links                |
| `DB_NAME`                   | PostgreSQL database name                              |
| `DB_USER`                   | PostgreSQL database user                              |
| `DB_PASSWORD`               | PostgreSQL database password                          |
| `DB_HOST`                   | PostgreSQL database host                              |
| `DB_PORT`                   | PostgreSQL database port                              |
| `REDIS_LOCATION`            | Redis cache location                                  |
| `REDIS_HOST`                | Redis host                                            |
| `REDIS_PORT`                | Redis port                                            |
| `REDIS_DB`                  | Redis database index                                  |
| `EMAIL_HOST`                | SMTP host                                             |
| `EMAIL_PORT`                | SMTP port                                             |
| `EMAIL_HOST_USER`           | SMTP user                                             |
| `EMAIL_HOST_PASSWORD`       | SMTP password                                         |
| `EMAIL_USE_TLS`             | Enables TLS for SMTP email delivery                   |
| `EMAIL_USE_SSL`             | Enables SSL for SMTP email delivery                   |
| `DEFAULT_FROM_EMAIL`        | Default sender address                                |

## Project Structure

The backend currently contains the Django core project and two prepared apps.

```text
backend/
├── auth_app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── templates/
│   │   └── auth_app/
│   │       └── emails/
│   │           ├── activation_email.html
│   │           └── password_reset_email.html
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── mixins.py
│   │   ├── test_activation_api.py
│   │   ├── test_login_api.py
│   │   ├── test_logout_api.py
│   │   ├── test_password_confirm_api.py
│   │   ├── test_password_reset_api.py
│   │   ├── test_registration_api.py
│   │   └── test_token_refresh_api.py
│   ├── admin.py
│   ├── apps.py
│   └── models.py
├── videos_app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── mixins.py
│   │   ├── test_video_list_api.py
│   │   ├── test_video_manifest_api.py
│   │   └── test_video_segment_api.py
│   ├── admin.py
│   ├── apps.py
│   └── models.py
├── core/
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

The frontend and backend are separated projects.

## Database Models

The project currently includes one project-specific database model.

### `videos_app.Video`

The `Video` model stores metadata used by the video API endpoints.

Current fields:

* `title`
* `description`
* `thumbnail_url`
* `category`
* `created_at`

The model is currently used by the video API test coverage to prepare video metadata and connect test videos with generated HLS manifest and HLS segment files.

HLS manifest files and HLS segment files are not stored directly in the database. They are expected to be stored as media files under `MEDIA_ROOT` and resolved through a defined path structure during API handling.

Current expected HLS media structure:

```text
MEDIA_ROOT/
└── videos/
    └── <video_id>/
        ├── 480p/
        │   ├── index.m3u8
        │   ├── 000.ts
        │   └── ...
        ├── 720p/
        │   ├── index.m3u8
        │   ├── 000.ts
        │   └── ...
        └── 1080p/
            ├── index.m3u8
            ├── 000.ts
            └── ...
```

The `Video` model is not final yet. Additional fields may be added later when video upload, thumbnail handling, processing status, conversion jobs or production media storage are implemented.

Additional database structures are provided by:

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

The backend currently provides authentication endpoints and the first video metadata endpoint.

### Authentication Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/api/register/` | Creates an inactive user account and sends an activation email |
| `GET` | `/api/activate/<uidb64>/<token>/` | Activates a user account with an email activation token |
| `POST` | `/api/login/` | Authenticates an active user and sets JWT cookies |
| `POST` | `/api/logout/` | Blacklists the refresh token and deletes authentication cookies |
| `POST` | `/api/token/refresh/` | Refreshes the access token from the refresh token cookie |
| `POST` | `/api/password_reset/` | Sends a password reset email when the account exists |
| `POST` | `/api/password_confirm/<uidb64>/<token>/` | Sets a new password after token validation |

### Video Endpoints

| Method | Endpoint | Description | Status |
| ------ | -------- | ----------- | ------ |
| `GET` | `/api/video/` | Returns authenticated video metadata ordered by creation date descending | Implemented |
| `GET` | `/api/video/<int:movie_id>/<str:resolution>/index.m3u8` | Returns an HLS manifest file for a video and resolution | Planned |
| `GET` | `/api/video/<int:movie_id>/<str:resolution>/<str:segment>/` | Returns an HLS video segment file for a video and resolution | Planned |

## Authentication

The authentication app is implemented with Django REST Framework and SimpleJWT.

Authentication uses HttpOnly cookies instead of returning JWT tokens directly to the frontend after login.

Cookie names:

* `access_token`
* `refresh_token`

Implemented authentication behavior:

* users register with email, password and password confirmation
* registered users are inactive until account activation
* activation emails contain frontend activation links
* login authenticates active users and sets JWT cookies
* logout blacklists the refresh token and deletes authentication cookies
* token refresh reads the refresh token from the cookie and sets a new access token cookie
* password reset responses stay neutral to avoid account enumeration
* password reset emails contain frontend password confirmation links
* password confirmation validates the token and stores the new password
* HTML email templates are rendered with plain text fallbacks

The HTML email templates are located under:

```text
auth_app/templates/auth_app/emails/
├── activation_email.html
└── password_reset_email.html
```

## Testing

The project uses pytest and pytest-django.

The test structure is organized per API endpoint. Each endpoint has its own dedicated test file.

The default Django `tests.py` files were removed because the project uses structured pytest test packages instead.

Current test coverage includes authentication endpoints and video endpoints.

| App | Test file | Tests |
| --- | --- | ---: |
| `auth_app` | `auth_app/tests/test_activation_api.py` | 6 |
| `auth_app` | `auth_app/tests/test_login_api.py` | 13 |
| `auth_app` | `auth_app/tests/test_logout_api.py` | 6 |
| `auth_app` | `auth_app/tests/test_password_confirm_api.py` | 9 |
| `auth_app` | `auth_app/tests/test_password_reset_api.py` | 5 |
| `auth_app` | `auth_app/tests/test_registration_api.py` | 16 |
| `auth_app` | `auth_app/tests/test_token_refresh_api.py` | 8 |
| `videos_app` | `videos_app/tests/test_video_list_api.py` | 7 |
| `videos_app` | `videos_app/tests/test_video_manifest_api.py` | 8 |
| `videos_app` | `videos_app/tests/test_video_segment_api.py` | 9 |
| **Total** | **10 test files** | **87** |

The tests currently define the expected API behavior. Some tests are expected to fail during the TDD phase until the related serializers, views, permissions and services are implemented.

## Running Tests

Tests should be executed inside the Docker container because the project database host `db` is resolved inside the Docker Compose network.

```bash
# Run the full test suite
docker-compose exec web python -m pytest -v

# Run all authentication app tests
docker-compose exec web python -m pytest auth_app/tests -v

# Run all video app tests
docker-compose exec web python -m pytest videos_app/tests -v

# Run a single authentication test file
docker-compose exec web python -m pytest auth_app/tests/test_registration_api.py -v

# Run a single video test file
docker-compose exec web python -m pytest videos_app/tests/test_video_list_api.py -v
```

If `docker-compose` is not available, use the newer Docker Compose syntax:

```bash
# Run the full test suite
docker compose exec web python -m pytest -v

# Run all authentication app tests
docker compose exec web python -m pytest auth_app/tests -v

# Run all video app tests
docker compose exec web python -m pytest videos_app/tests -v

# Run a single authentication test file
docker compose exec web python -m pytest auth_app/tests/test_registration_api.py -v

# Run a single video test file
docker compose exec web python -m pytest videos_app/tests/test_video_list_api.py -v
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
* auth_app created
* videos_app created
* API folders prepared for both apps
* base API files added for serializers, views, urls and permissions
* placeholder API views added for planned endpoints
* authentication API routes prepared
* video API routes prepared
* app API URLs included in core/urls.py
* pytest configuration added
* pytest test packages prepared for both apps
* endpoint-based test files created
* default Django tests.py files removed
* no project-specific API business logic has been implemented yet
* authentication API endpoint tests added
* registration API tests added
* account activation API tests added
* login API tests added
* logout API tests added
* token refresh API tests added
* password reset API tests added
* password confirm API tests added
* `Video` model added in `videos_app/models.py`
* video list API tests added
* video manifest API tests added
* video segment API tests added
* reusable authentication test helpers added
* reusable video test helpers added
* Docker-based pytest commands documented
* current prepared test count documented
* authentication API routes implemented
* registration API implemented
* account activation API implemented
* login API implemented
* logout API implemented
* token refresh API implemented
* password reset API implemented
* password confirm API implemented
* JWT authentication uses HttpOnly cookies
* access tokens are stored in the `access_token` cookie
* refresh tokens are stored in the `refresh_token` cookie
* refresh tokens are blacklisted on logout
* account activation emails implemented
* password reset emails implemented
* HTML email templates added for activation and password reset emails
* plain text email fallbacks kept for authentication emails
* frontend email links configured through `FRONTEND_BASE_URL`
* generated local email preview files ignored
* cookie-based JWT authentication class added for protected video endpoints
* video metadata serializer added
* authenticated `GET /api/video/` endpoint implemented
* video list response returns documented metadata fields
* video list response is ordered by creation date descending
* video list endpoint verified with passing tests
