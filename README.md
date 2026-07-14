# Videoflix Backend

Videoflix Backend is a Django REST Framework backend for a Netflix-inspired video platform.

The backend provides user registration, email-based account activation, cookie-based JWT authentication, password reset functionality, authenticated video metadata endpoints and HLS video streaming in multiple resolutions.

Videos can be uploaded through the Django admin and converted asynchronously into HLS output files by Django RQ and FFmpeg.

The project uses a Docker-based setup with PostgreSQL, Redis, Django RQ, Gunicorn and WhiteNoise. The frontend and backend are maintained as separate projects and communicate through a REST API.

## Setup

Run the following commands to set up the project locally.

```bash
# Clone repository
git clone https://github.com/Juergen-Malinowski/Backend-Project-Videoflix.git

# Open project folder
cd Backend-Project-Videoflix

# Create local environment file
cp .env.template .env
```

Open the newly created `.env` file and replace the template values with your local configuration.

At minimum, configure:

* Django secret key and debug settings
* allowed hosts and trusted frontend origins
* PostgreSQL credentials
* Redis connections
* Django admin credentials
* SMTP credentials
* frontend base URL

Never commit the local `.env` file or real credentials.

Build and start the Docker containers:

```bash
docker-compose up --build
```

If `docker-compose` is not available, use the newer Docker Compose syntax:

```bash
docker compose up --build
```

The Docker entrypoint automatically:

* waits until PostgreSQL is available
* collects static files
* applies database migrations
* creates the Django superuser from environment variables
* starts the Django RQ worker
* starts Gunicorn on port `8000`

The backend is then available at:

```text
http://127.0.0.1:8000
```

Open the Django admin at:

```text
http://127.0.0.1:8000/admin/
```

The Django superuser is created automatically from the following variables defined in the local `.env` file:

```env
DJANGO_SUPERUSER_USERNAME=your_admin_username
DJANGO_SUPERUSER_PASSWORD=your_admin_password
DJANGO_SUPERUSER_EMAIL=your_admin_email@example.com
```

These values are read by `backend.entrypoint.sh` when the Docker container starts.

For local frontend integration, start the compatible Developer Akademie frontend separately:

[Developer Akademie Videoflix Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)

The recommended local frontend address is:

```text
http://127.0.0.1:5500
```

Ensure that `FRONTEND_BASE_URL` and `CSRF_TRUSTED_ORIGINS` use the same frontend origin.

## Table of Contents

* [Features](#features)
* [Tech Stack](#tech-stack)
* [Environment Variables](#environment-variables)
* [Docker Architecture](#docker-architecture)
* [Project Structure](#project-structure)
* [Database Model](#database-model)
  * [`videos_app.Video`](#videos_appvideo)
* [Django Admin and HLS Workflow](#django-admin-and-hls-workflow)
* [Media Structure](#media-structure)
* [API Endpoints](#api-endpoints)
  * [Authentication Endpoints](#authentication-endpoints)
  * [Video Endpoints](#video-endpoints)
* [Authentication and Email Delivery](#authentication-and-email-delivery)
* [Frontend Integration](#frontend-integration)
* [Testing](#testing)
* [Running Tests](#running-tests)
* [Docker Commands](#docker-commands)
* [Current Implementation Status](#current-implementation-status)

## Features

* User registration with email and password confirmation
* Email-based account activation before the first login
* Secure login with JWT access and refresh tokens stored in HttpOnly cookies
* Token refresh and secure logout with refresh-token blacklisting
* Password reset through responsive HTML emails with plain text fallbacks
* Neutral authentication responses to reduce account enumeration risks
* Authenticated video metadata API
* Video ordering by creation date in descending order
* Video upload through the Django admin
* Asynchronous HLS conversion with Django RQ and FFmpeg
* HLS output in `480p`, `720p` and `1080p`
* HLS manifest and segment delivery through protected API endpoints
* Processing states for pending, processing, ready and failed conversions
* Stored processing errors and retry support for failed conversions
* PostgreSQL database integration
* Redis-backed Django cache configuration
* Redis-based RQ job queue
* Docker-based development and runtime environment
* Automatic database migrations and Django superuser creation
* Separate frontend and backend projects communicating through a REST API

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Redis
* Django RQ
* FFmpeg
* SimpleJWT
* django-cors-headers
* django-redis
* Gunicorn
* WhiteNoise
* Docker
* Docker Compose
* pytest
* pytest-django

## Environment Variables

Environment variables are loaded from the local `.env` file.

Create this file from `.env.template` during setup and replace all placeholder values with your own local configuration.

The `.env` file must never be committed.

| Name | Purpose |
| --- | --- |
| `DJANGO_SUPERUSER_USERNAME` | Username for the automatically created Django admin account |
| `DJANGO_SUPERUSER_PASSWORD` | Password for the automatically created Django admin account |
| `DJANGO_SUPERUSER_EMAIL` | Email address for the automatically created Django admin account |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enables or disables Django debug mode |
| `ALLOWED_HOSTS` | Hosts allowed to access the backend |
| `CSRF_TRUSTED_ORIGINS` | Trusted frontend origins for CSRF protection |
| `FRONTEND_BASE_URL` | Frontend base URL used in activation and password reset emails |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL database user |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_HOST` | PostgreSQL database host |
| `DB_PORT` | PostgreSQL database port |
| `REDIS_LOCATION` | Redis connection used by the Django caching layer |
| `REDIS_HOST` | Redis host used by Django RQ |
| `REDIS_PORT` | Redis port used by Django RQ |
| `REDIS_DB` | Redis database index used by Django RQ |
| `EMAIL_HOST` | SMTP server hostname |
| `EMAIL_PORT` | SMTP server port |
| `EMAIL_HOST_USER` | SMTP account username |
| `EMAIL_HOST_PASSWORD` | SMTP account password |
| `EMAIL_USE_TLS` | Enables STARTTLS for SMTP delivery |
| `EMAIL_USE_SSL` | Enables SSL/TLS for SMTP delivery |
| `DEFAULT_FROM_EMAIL` | Default sender address for outgoing emails |

For local development, use the same frontend origin for `FRONTEND_BASE_URL` and `CSRF_TRUSTED_ORIGINS`.

Example:

```env
FRONTEND_BASE_URL=http://127.0.0.1:5500
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500
```

Redis uses separate database indexes for caching and background jobs:

```env
REDIS_LOCATION=redis://redis:6379/1
REDIS_DB=0
```

Redis database `1` is configured for the Django caching layer. Redis database `0` is used by Django RQ.

Only one SMTP encryption mode may be enabled at the same time.

Example for SMTP over SSL/TLS:

```env
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
```

Example for SMTP with STARTTLS:

```env
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
```

## Docker Architecture

The project runs with Docker Compose and uses three services:

* `web` for Django, Gunicorn, the Django RQ worker and FFmpeg
* `db` for PostgreSQL
* `redis` for Django RQ and the Django caching layer

The `web` service depends on PostgreSQL and Redis.

The Docker entrypoint starts the required backend processes in this order:

```text
Wait for PostgreSQL
→ collect static files
→ create and apply migrations
→ create the Django superuser
→ start the Django RQ worker
→ start Gunicorn
```

The Django RQ worker runs as a background process inside the `web` container and listens to the `default` queue.

Redis is shared by two application areas:

```text
Redis database 0
└── Django RQ job queue

Redis database 1
└── Django caching layer
```

PostgreSQL stores all persistent application data, including users, videos, processing states and token blacklist records.

Uploaded source videos and generated HLS files are stored in the named Docker volume `videoflix_media`.

Static files are stored in the named Docker volume `videoflix_static`.

The Docker Compose setup uses the following named volumes:

```text
postgres_data
redis_data
videoflix_media
videoflix_static
```

These volumes preserve database, Redis, media and static data across normal container restarts.

## Project Structure

```text
Backend-Project-Videoflix/
├── auth_app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── authentication.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── migrations/
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
│   ├── __init__.py
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
│   ├── migrations/
│   ├── services/
│   │   ├── __init__.py
│   │   └── hls.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── mixins.py
│   │   ├── test_hls_processing.py
│   │   ├── test_video_admin.py
│   │   ├── test_video_cache.py
│   │   ├── test_video_list_api.py
│   │   ├── test_video_manifest_api.py
│   │   ├── test_video_model.py
│   │   ├── test_video_segment_api.py
│   │   └── test_video_tasks.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── cache.py
│   ├── models.py
│   └── tasks.py
├── core/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env.template
├── .gitignore
├── backend.Dockerfile
├── backend.entrypoint.sh
├── docker-compose.yml
├── manage.py
├── pytest.ini
├── README.md
└── requirements.txt
```

The frontend is maintained in a separate repository and is not included in this backend project.

## Database Model

The project contains one project-specific database model.

### `videos_app.Video`

The `Video` model stores video metadata, the original source file and the current HLS processing state.

| Field | Description |
| --- | --- |
| `title` | Video title |
| `description` | Video description |
| `thumbnail_url` | URL of the video thumbnail |
| `category` | Video category or genre |
| `source_file` | Uploaded original video file |
| `processing_status` | Current HLS conversion state |
| `processing_error` | Stored error message from a failed conversion |
| `created_at` | Date and time when the video record was created |

Available processing states:

* `pending` – the video is waiting for conversion
* `processing` – the HLS conversion is currently running
* `ready` – the HLS output was created successfully
* `failed` – the HLS conversion failed

Uploaded source files are first stored temporarily and moved after the initial database save to:

```text
MEDIA_ROOT/videos/<video_id>/source/<original_filename>
```

The original source file remains available after successful or failed HLS processing.

Generated HLS manifests and segments are stored as media files and are not stored directly in the database.

Additional database structures are provided by:

* Django authentication
* Django admin
* Django sessions
* Django RQ
* SimpleJWT token blacklist

## Django Admin and HLS Workflow

The `Video` model is registered in the Django admin under the app label `Videoverwaltung`.

The admin interface provides:

* video metadata management
* original video file upload
* filtering by category, processing status and creation date
* search by title, description and category
* processing status display
* shortened processing error previews
* HLS conversion actions
* retry support for failed conversions

Available admin actions:

* `Convert selected videos to HLS`
* `Retry failed HLS conversions`

The HLS processing workflow is:

```text
Upload original video
→ save video record
→ move source file to the final source directory
→ processing status: pending
→ select video in the Django admin
→ start HLS conversion action
→ enqueue Django RQ background job
→ processing status: processing
→ run FFmpeg conversion
→ processing status: ready or failed
```

A successful conversion creates HLS output for:

* `480p`
* `720p`
* `1080p`

If the conversion succeeds:

* the processing status changes to `ready`
* the processing error is cleared
* the original source file remains available
* generated manifests and segments are preserved

If the conversion fails:

* the processing status changes to `failed`
* the exception message is stored in `processing_error`
* partially generated HLS resolution folders are removed
* the original source file remains available
* the conversion can be started again through the retry action

Only videos with the processing status `ready` are returned by the video list API and allowed to serve HLS manifests and segments.

## Media Structure

Uploaded source files and generated HLS files are stored under `MEDIA_ROOT`.

```text
MEDIA_ROOT/
└── videos/
    └── <video_id>/
        ├── source/
        │   └── <original_filename>
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

The `source` directory stores the original uploaded video file.

Each resolution directory contains:

* one HLS manifest named `index.m3u8`
* one or more MPEG transport stream segments named with a three-digit pattern such as `000.ts`, `001.ts` and `002.ts`

FFmpeg creates HLS segments with a target duration of 10 seconds.

Generated HLS folders can be removed after a failed conversion without deleting the original source file.

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/register/` | Creates an inactive user account and sends an activation email |
| `GET` | `/api/activate/<uidb64>/<token>/` | Activates a user account with a valid activation token |
| `POST` | `/api/login/` | Authenticates an active user and sets JWT cookies |
| `POST` | `/api/logout/` | Blacklists the refresh token and deletes authentication cookies |
| `POST` | `/api/token/refresh/` | Creates a new access token from the refresh token cookie |
| `POST` | `/api/password_reset/` | Sends a password reset email when the account exists |
| `POST` | `/api/password_confirm/<uidb64>/<token>/` | Validates the reset token and stores a new password |

### Video Endpoints

All video endpoints require authentication.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/video/` | Returns metadata for all videos with the processing status `ready`, ordered by creation date descending |
| `GET` | `/api/video/<int:movie_id>/<str:resolution>/index.m3u8` | Returns the HLS manifest for a ready video and supported resolution |
| `GET` | `/api/video/<int:movie_id>/<str:resolution>/<str:segment>/` | Returns an HLS transport stream segment for a ready video and supported resolution |

Supported HLS resolutions:

* `480p`
* `720p`
* `1080p`

The video list response contains:

* `id`
* `created_at`
* `title`
* `description`
* `thumbnail_url`
* `category`

The manifest endpoint returns:

```text
Content-Type: application/vnd.apple.mpegurl
```

The segment endpoint returns:

```text
Content-Type: video/MP2T
```

Videos with the processing status `pending`, `processing` or `failed` cannot serve HLS manifests or segments.

## Authentication and Email Delivery

Authentication is implemented with SimpleJWT and HttpOnly cookies.

After a successful login, the backend sets:

* an `access_token` cookie
* a `refresh_token` cookie

The access token is used for authenticated API requests.

The refresh token is used by `/api/token/refresh/` to create a new access token without requiring the user to log in again.

Authentication cookies are:

* inaccessible to JavaScript through `HttpOnly`
* deleted during logout
* validated by the custom cookie-based JWT authentication class

During logout, the refresh token is added to the SimpleJWT blacklist before both authentication cookies are removed.

Newly registered users are inactive until they activate their account through the link sent by email.

The registration workflow is:

1. The user submits an email address, password and password confirmation.
2. The backend creates an inactive user account.
3. The backend sends an activation email.
4. The frontend extracts the user ID and token from the activation link.
5. The frontend calls the backend activation endpoint.
6. The backend activates the account when the token is valid.

The password reset workflow is:

1. The user submits an email address.
2. The backend returns a neutral response regardless of whether the account exists.
3. If the account exists, the backend sends a password reset email.
4. The frontend extracts the user ID and token from the reset link.
5. The user submits and confirms a new password.
6. The backend validates the token and stores the new password.

Activation and password reset emails include:

* a responsive HTML version
* a plain text fallback
* a frontend URL built from `FRONTEND_BASE_URL`
* a time-limited Django token

SMTP delivery is configured through environment variables.

Only one SMTP encryption mode may be enabled:

* SSL/TLS with `EMAIL_USE_SSL=True`
* STARTTLS with `EMAIL_USE_TLS=True`

## Frontend Integration

The frontend is maintained as a separate project and communicates with the backend through the REST API.

Compatible frontend repository:

[Developer Akademie Videoflix Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)

For local development, the frontend is typically served with a local development server at:

```text
http://127.0.0.1:5500
```

The backend is typically available at:

```text
http://127.0.0.1:8000
```

The frontend origin must match the values configured in:

* `FRONTEND_BASE_URL`
* `CSRF_TRUSTED_ORIGINS`

Example:

```env
FRONTEND_BASE_URL=http://127.0.0.1:5500
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500
```

Authentication tokens are stored in HttpOnly cookies.

Frontend requests that require authentication must therefore include credentials.

Example with `fetch`:

```javascript
fetch("http://127.0.0.1:8000/api/video/", {
    method: "GET",
    credentials: "include",
});
```

Activation and password reset links point to frontend pages.

The frontend reads the user ID and token from the URL parameters and sends them to the corresponding backend endpoint.

The frontend has been tested successfully with:

* user registration
* account activation
* login
* token-based authentication
* password reset
* authenticated video list loading
* HLS video playback in multiple resolutions

## Testing

The project uses `pytest` and `pytest-django` for automated testing.

The complete test suite contains:

* 148 collected tests
* 148 passed tests
* 15 test files
* total execution time: 40.60 seconds

Test distribution:

| Application | Test files | Tests |
| --- | ---: | ---: |
| `auth_app` | 7 | 73 |
| `videos_app` | 8 | 75 |
| **Total** | **15** | **148** |

The authentication tests cover:

* user registration
* duplicate email validation
* password confirmation validation
* activation email delivery
* account activation
* login
* cookie-based JWT authentication
* token refresh
* logout
* refresh-token blacklisting
* password reset email delivery
* password reset confirmation
* invalid and expired token handling
* neutral authentication responses
* HTML email content
* plain text email fallbacks
* frontend activation and reset links

The video tests cover:

* video model behavior
* source file handling
* HLS processing
* FFmpeg command generation
* processing status changes
* processing error handling
* cleanup after failed conversions
* Django admin configuration
* admin conversion actions
* retry actions
* Django RQ task behavior
* Redis-backed video list caching
* cache invalidation
* authenticated video list access
* video list serialization
* ready-video filtering
* creation-date ordering
* HLS manifest delivery
* HLS segment delivery
* supported resolution validation
* missing file handling
* unauthorized access handling
* internal error handling

Tests use isolated temporary media directories where file-system operations are required.

External processes and integrations such as FFmpeg, Django RQ, Redis and email delivery are mocked where appropriate.

The complete workflow was additionally verified manually through the Django admin and the compatible frontend, including real HLS conversion, account activation, login, password reset and video playback.

## Running Tests

The test suite is organized by application.

```text
auth_app/
└── tests/
    ├── test_activation_api.py
    ├── test_login_api.py
    ├── test_logout_api.py
    ├── test_password_confirm_api.py
    ├── test_password_reset_api.py
    ├── test_registration_api.py
    └── test_token_refresh_api.py

videos_app/
└── tests/
    ├── test_hls_processing.py
    ├── test_video_admin.py
    ├── test_video_cache.py
    ├── test_video_list_api.py
    ├── test_video_manifest_api.py
    ├── test_video_model.py
    ├── test_video_segment_api.py
    └── test_video_tasks.py
```

Run all tests:

```bash
docker-compose exec web pytest
```

Run all authentication tests:

```bash
docker-compose exec web pytest auth_app/tests/
```

Run all video tests:

```bash
docker-compose exec web pytest videos_app/tests/
```

Run a single test file:

```bash
docker-compose exec web pytest auth_app/tests/test_registration_api.py
```

Example for a video test file:

```bash
docker-compose exec web pytest videos_app/tests/test_video_list_api.py
```

If `docker-compose` is not available, replace it with `docker compose` in the commands above.

## Docker Commands

Build and start all services:

```bash
docker-compose up --build
```

Start all services without rebuilding the images:

```bash
docker-compose up
```

Start all services in detached mode:

```bash
docker-compose up -d
```

Stop and remove the running containers:

```bash
docker-compose down
```

Restart the Django backend container:

```bash
docker-compose restart web
```

Open a shell inside the Django backend container:

```bash
docker-compose exec web bash
```

Run a Django management command inside the backend container:

```bash
docker-compose exec web python manage.py <command>
```

Example:

```bash
docker-compose exec web python manage.py showmigrations
```

View logs from all services:

```bash
docker-compose logs
```

Follow the Django backend logs:

```bash
docker-compose logs -f web
```

View the running containers:

```bash
docker-compose ps
```

Stop the containers and remove the named volumes:

```bash
docker-compose down -v
```

This command deletes persistent PostgreSQL, Redis, media and static volume data and should therefore be used with caution.

If `docker-compose` is not available, replace it with `docker compose` in the commands above.

## Current Implementation Status

The Videoflix backend is fully implemented and operational.

Completed authentication functionality:

* user registration
* duplicate email and username validation
* password confirmation validation
* inactive account creation
* account activation through email
* cookie-based JWT login
* access-token refresh
* secure logout
* refresh-token blacklisting
* password reset email delivery
* password reset confirmation
* responsive HTML emails
* plain text email fallbacks
* configurable frontend activation and reset links
* neutral responses for security-sensitive authentication requests

Completed video functionality:

* video metadata model
* source video upload through the Django admin
* final source-file storage based on the video ID
* processing states for pending, processing, ready and failed videos
* asynchronous processing through Django RQ
* FFmpeg-based HLS conversion
* HLS output in `480p`, `720p` and `1080p`
* processing error storage
* cleanup after failed conversions
* retry support for failed conversions
* authenticated video list endpoint
* ready-video filtering
* video ordering by creation date
* protected HLS manifest endpoint
* protected HLS segment endpoint
* supported-resolution validation
* Redis-backed video list caching
* cache invalidation after relevant video changes

Completed infrastructure:

* PostgreSQL database integration
* Redis integration for Django RQ
* separate Redis database for the Django caching layer
* Docker Compose configuration
* automatic PostgreSQL availability check
* automatic static-file collection
* automatic migration creation and execution
* automatic Django superuser creation
* automatic Django RQ worker startup
* Gunicorn application server
* WhiteNoise static-file delivery
* configurable SMTP delivery
* persistent Docker volumes for database, Redis, media and static files

Verification status:

* 148 automated tests collected
* 148 automated tests passed
* complete authentication workflow verified with the frontend
* real SMTP delivery verified
* account activation verified through email
* password reset verified through email
* real HLS conversion verified with FFmpeg
* generated HLS manifests and segments verified
* authenticated video playback verified with the compatible frontend

The backend is ready for final documentation review, repository cleanup and deployment preparation.
