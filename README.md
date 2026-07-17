# Videoflix Backend

Videoflix Backend is a Django REST Framework backend for a Netflix-inspired video platform.

The backend provides user registration, email-based account activation, cookie-based JWT authentication, token refresh, secure logout, password reset functionality, authenticated video metadata endpoints and protected HLS video streaming in multiple resolutions.

Videos can be uploaded through the Django admin. After a new video with a source file is saved, the backend automatically starts asynchronous HLS processing through Django RQ and FFmpeg after the database transaction has been committed.

The video processing workflow generates HLS output files in multiple resolutions and creates a local thumbnail image for each successfully processed video. Only videos with the processing status `ready` are exposed through the video list API and allowed to serve HLS manifests and segments.

The project uses a Docker-based setup with PostgreSQL, Redis, a dedicated Django RQ worker service, Gunicorn, WhiteNoise and FFmpeg. The frontend and backend are maintained as separate projects and communicate through a REST API.

The entire backend was developed using a Test-Driven Development workflow, with tests written before each functional implementation and used for immediate verification throughout development.

## Setup

### Prerequisites

Before setting up the backend, ensure that the following software is installed:

* Git
* Docker Desktop on Windows or macOS, or Docker Engine on Linux
* Docker Compose

Docker Desktop or the Docker service must be running before the containers are built and started.

Python, PostgreSQL, Redis and FFmpeg do not need to be installed separately on the host system because they are provided through Docker.

### Clone the Backend Repository

Clone the backend repository:

```bash
git clone https://github.com/Juergen-Malinowski/Backend-Project-Videoflix.git
```

Open the project directory:

```bash
cd Backend-Project-Videoflix
```

### Create the Environment File

On Linux, macOS, Git Bash or WSL, create the local `.env` file with:

```bash
cp .env.template .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.template .env
```

On Windows Command Prompt, use:

```cmd
copy .env.template .env
```

Open the newly created `.env` file and replace the template values with your own local configuration.

Generate a unique Django `SECRET_KEY`.

If Python is installed locally, use:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

If Python is not installed locally, generate the key through Docker Compose:

```bash
docker compose run --rm web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

With the older Docker Compose syntax, use:

```bash
docker-compose run --rm web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Insert the generated value into the `.env` file:

```env
SECRET_KEY="your_generated_secret_key"
```

Every developer must generate an individual `SECRET_KEY`.

The `.env` file must never be committed.

If a `SECRET_KEY` has been exposed publicly, replace it immediately.

At minimum, configure:

* a unique Django `SECRET_KEY`
* the desired `DEBUG` value
* allowed backend hosts
* trusted frontend origins
* PostgreSQL database credentials
* Redis connections
* Django admin credentials
* SMTP credentials
* the frontend base URL

The following values must not remain unchanged in a real environment:

```env
DJANGO_SUPERUSER_USERNAME=your_admin_username
DJANGO_SUPERUSER_PASSWORD=your_secure_admin_password
DJANGO_SUPERUSER_EMAIL=your_admin_email@example.com

SECRET_KEY="your_generated_secret_key"

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_secure_database_password
DB_HOST=db
DB_PORT=5432
```

Redis is configured through Docker and normally uses:

```env
REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0
```

To use account activation and password reset email delivery, configure valid SMTP credentials.

Example for SMTP over SSL/TLS:

```env
EMAIL_HOST=your_smtp_server
EMAIL_PORT=465
EMAIL_HOST_USER=your_email_address
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=your_email_address
```

Example for SMTP with STARTTLS:

```env
EMAIL_HOST=your_smtp_server
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_address
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your_email_address
```

Only one SMTP encryption mode may be enabled at the same time.

### Build and Start the Backend

Ensure that Docker Desktop or the Docker service is running.

Build the Docker images and start all containers:

```bash
docker-compose up --build
```

If `docker-compose` is not available, use the newer Docker Compose syntax:

```bash
docker compose up --build
```

The command runs in the foreground and displays the container logs.

Stop the running containers with:

```text
Ctrl+C
```

The Docker entrypoint of the `web` service automatically:

* waits until PostgreSQL is available
* collects static files
* creates and applies database migrations
* creates the Django superuser from environment variables
* starts Gunicorn on port `8000`

The Django RQ worker runs in a dedicated `worker` service and listens to the `default` queue.

During the first build, Docker installs all Python dependencies and the required system packages, including FFmpeg.

### Open the Backend

The backend is available at:

```text
http://127.0.0.1:8000
```

The Django admin is available at:

```text
http://127.0.0.1:8000/admin/
```

Log in with the credentials configured in:

```env
DJANGO_SUPERUSER_USERNAME=your_admin_username
DJANGO_SUPERUSER_PASSWORD=your_secure_admin_password
```

### Start the Backend Later

After the initial build, start the existing containers without rebuilding the images:

```bash
docker-compose up
```

Start them in detached mode:

```bash
docker-compose up -d
```

With the newer Docker Compose syntax, use:

```bash
docker compose up
```

or:

```bash
docker compose up -d
```

## Frontend Setup

The frontend is maintained in a separate repository and must be started independently from the backend.

The frontend version used and tested with this backend is available here:

[Juergen Malinowski Videoflix Frontend](https://github.com/Juergen-Malinowski/Frontend-Project-Videoflix)

The frontend project is based on the original Videoflix frontend provided by the Developer Akademie:

[Original Developer Akademie Videoflix Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)

### Frontend Prerequisites

Before setting up the frontend, ensure that the following software is installed:

* Git
* Visual Studio Code
* the VS Code Live Server extension

The Videoflix frontend is a static frontend project and does not require a separate package installation.

### Clone the Frontend Repository

Open a second terminal outside the backend project directory and clone the frontend repository:

```bash
git clone https://github.com/Juergen-Malinowski/Frontend-Project-Videoflix.git
```

Open the frontend project directory:

```bash
cd Frontend-Project-Videoflix
```

Open the project in Visual Studio Code:

```bash
code .
```

If the `code` command is unavailable, open Visual Studio Code manually and select the cloned `Frontend-Project-Videoflix` folder through `File` → `Open Folder`.

### Start the Frontend

Ensure that the Videoflix backend is already running at:

```text
http://127.0.0.1:8000
```

In Visual Studio Code:

1. Open `index.html`.
2. Right-click inside the file.
3. Select `Open with Live Server`.

The frontend should be available at:

```text
http://127.0.0.1:5500
```

The exact Live Server port must match the frontend origin configured in the backend `.env` file:

```env
FRONTEND_BASE_URL=http://127.0.0.1:5500
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5500
```

Backend and frontend must run at the same time for registration, authentication, email links, video list loading and HLS playback to work.

Use the same host format consistently. Do not mix `localhost` and `127.0.0.1` unless both origins are included in `CSRF_TRUSTED_ORIGINS`.

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

## Features

* User registration with email and password confirmation
* Email-based account activation before the first login
* Secure login with JWT access and refresh tokens stored in HttpOnly cookies
* Token refresh and secure logout with refresh-token blacklisting
* Authentication cookie lifetimes derived from `SIMPLE_JWT` settings
* Password reset through responsive HTML emails with plain text fallbacks
* Neutral authentication responses to reduce account enumeration risks
* Authenticated video metadata API
* Video ordering by creation date in descending order
* Video upload through the Django admin
* Automatic asynchronous HLS conversion with Django RQ and FFmpeg after video creation
* Dedicated Docker worker service for background video processing
* Local thumbnail generation during video processing
* Absolute `thumbnail_url` values for frontend media access
* HLS output in `480p`, `720p` and `1080p`
* HLS manifest and segment delivery through protected API endpoints
* Processing states for pending, processing, ready and failed conversions
* Stored processing errors for failed conversions
* Cleanup of uploaded source files, generated HLS folders and generated thumbnails after failed processing
* Automatic removal of a video's complete media directory when the video record is deleted
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
* Pillow
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

The project runs with Docker Compose and uses four services:

* `web` for Django, Gunicorn, API requests, admin access and static-file delivery
* `worker` for Django RQ background jobs and FFmpeg-based video processing
* `db` for PostgreSQL
* `redis` for Django RQ and the Django caching layer

The `web` service depends on PostgreSQL and Redis.

The `worker` service also depends on PostgreSQL and Redis and listens to the Django RQ `default` queue.

The Docker entrypoint of the `web` service starts the required backend processes in this order:

```text
Wait for PostgreSQL
→ collect static files
→ create and apply migrations
→ create the Django superuser
→ start Gunicorn
```

The `worker` service starts the Django RQ worker directly and bypasses the backend entrypoint.

This prevents the worker container from running web-specific startup tasks such as static-file collection and migration handling.

Redis is shared by two application areas:

```text
Redis database 0
└── Django RQ job queue

Redis database 1
└── Django caching layer
```

PostgreSQL stores all persistent application data, including users, videos, processing states and token blacklist records.

Uploaded source videos, generated thumbnails and generated HLS files are stored in the named Docker volume `videoflix_media`.

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
│   │   ├── test_video_auto_processing.py
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

The `Video` model stores video metadata, the uploaded source file, the generated thumbnail file and the current HLS processing state.

| Field | Description |
| --- | --- |
| `title` | Video title |
| `description` | Video description |
| `thumbnail` | Generated local thumbnail image |
| `category` | Video category or genre |
| `source_file` | Uploaded original video file |
| `processing_status` | Current HLS conversion state |
| `processing_error` | Stored error message from a failed conversion |
| `created_at` | Date and time when the video record was created |

Available processing states:

* `pending` – the video is waiting for conversion
* `processing` – the HLS conversion is currently running
* `ready` – the HLS output and thumbnail were created successfully
* `failed` – the HLS conversion failed

Uploaded source files are first stored temporarily and moved after the initial database save to:

```text
MEDIA_ROOT/videos/<video_id>/source/<original_filename>
```

Generated thumbnails are stored as media files at:

```text
MEDIA_ROOT/videos/<video_id>/thumbnail/thumbnail.jpg
```

Generated HLS manifests and segments are stored as media files and are not stored directly in the database.

If processing succeeds, the source file, generated thumbnail and generated HLS output remain available.

If processing fails, the video record remains in the database with the processing status `failed`, the technical error is stored in `processing_error`, and uploaded or generated processing files are cleaned up.

When a video record is deleted, the complete media directory for that video is removed.

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
* generated thumbnail preview
* readonly processing status information
* readonly processing error information

The processing status and processing error fields are managed by the backend and are readonly in the Django admin.

Manual HLS conversion and retry actions are not exposed in the admin interface.

The HLS processing workflow is:

```text
Upload original video through the Django admin
→ save new video record
→ move source file to the final source directory
→ enqueue conversion job after the database transaction has been committed
→ processing status: processing
→ generate thumbnail with FFmpeg
→ generate HLS output with FFmpeg
→ processing status: ready or failed
```

A successful conversion creates:

* a generated thumbnail image
* HLS output for `480p`
* HLS output for `720p`
* HLS output for `1080p`

If the conversion succeeds:

* the processing status changes to `ready`
* the processing error is cleared
* the original source file remains available
* the generated thumbnail remains available
* generated manifests and segments are preserved
* the video becomes visible through the video list API
* protected HLS manifests and segments can be served

If the conversion fails:

* the processing status changes to `failed`
* the exception message is stored in `processing_error`
* uploaded source files are removed
* generated thumbnail files are removed
* partially generated HLS resolution folders are removed
* the failed video record remains available in the admin for inspection
* the video is not exposed through the video list API

Only videos with the processing status `ready` are returned by the video list API and allowed to serve HLS manifests and segments.

When a video record is deleted, the complete media directory for that video is removed.

## Media Structure

Uploaded source files, generated thumbnails and generated HLS files are stored under `MEDIA_ROOT`.

```text
MEDIA_ROOT/
└── videos/
    └── <video_id>/
        ├── source/
        │   └── <original_filename>
        ├── thumbnail/
        │   └── thumbnail.jpg
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

The `source` directory stores the original uploaded video file after the initial database save.

The `thumbnail` directory stores the generated thumbnail image created by FFmpeg during video processing.

Each resolution directory contains:

* one HLS manifest named `index.m3u8`
* one or more MPEG transport stream segments named with a three-digit pattern such as `000.ts`, `001.ts` and `002.ts`

FFmpeg creates HLS segments with a target duration of 10 seconds.

If video processing fails, uploaded source files, generated thumbnails and partially generated HLS folders are removed.

If a video record is deleted, the complete media directory for that video is removed.

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

The `thumbnail_url` field contains an absolute URL to the generated local thumbnail image.

Example:

```json
{
  "id": 1,
  "created_at": "2026-07-17T10:30:00Z",
  "title": "Example Video",
  "description": "Example description",
  "thumbnail_url": "http://127.0.0.1:8000/media/videos/1/thumbnail/thumbnail.jpg",
  "category": "Drama"
}
```

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
* configured with `SameSite=Lax`
* configured with lifetimes derived from the `SIMPLE_JWT` settings
* deleted during logout
* validated by the custom cookie-based JWT authentication class

The `access_token` cookie lifetime is derived from `SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]`.

The `refresh_token` cookie lifetime is derived from `SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]`.

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

[Juergen Malinowski Videoflix Frontend](https://github.com/Juergen-Malinowski/Frontend-Project-Videoflix)

This frontend is based on the original project provided by the Developer Akademie:

[Original Developer Akademie Videoflix Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Videoflix)

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

Authenticated frontend requests use HttpOnly cookies and must include `credentials: "include"`. The tested frontend refreshes the access token periodically through the backend refresh endpoint.

Example with `fetch`:

```javascript
fetch("http://127.0.0.1:8000/api/video/", {
    method: "GET",
    credentials: "include",
});
```

The video list API returns absolute `thumbnail_url` values so that the separately served frontend can load generated thumbnail images directly from the backend media URL.

Activation and password reset links point to frontend pages.

The frontend reads the user ID and token from the URL parameters and sends them to the corresponding backend endpoint.

The frontend has been tested successfully with:

* user registration
* account activation
* login
* token-based authentication
* password reset
* authenticated video list loading
* generated thumbnail loading
* HLS video playback in multiple resolutions
* authenticated frontend usage after access-cookie lifetime correction

## Testing

The entire backend was developed according to the Test-Driven Development approach.

For each functional area, the required tests were written first. The implementation was then developed incrementally until the corresponding tests passed. This provided immediate verification of every implemented behavior and helped ensure that the API documentation, backend logic and frontend requirements remained consistent throughout development.

The development cycle followed this pattern:

```text
Define the required behavior
→ write the corresponding tests
→ run the tests and verify that they fail
→ implement the functionality
→ run the tests again
→ refactor while keeping all tests passing
```

The project uses `pytest` and `pytest-django` for automated testing.

The complete test suite contains:

```text
185 collected tests
185 passed tests
16 test files
total execution time: 43.08 seconds
```

Test distribution:

| Application | Test files | Tests |
| ----------- | ---------: | ----: |
| auth_app | 7 | 75 |
| videos_app | 9 | 110 |
| Total | 16 | 185 |

The authentication tests cover:

* user registration
* duplicate email validation
* password confirmation validation
* activation email delivery
* account activation
* login
* cookie-based JWT authentication
* authentication cookie lifetime configuration
* token refresh
* refreshed access-token cookie lifetime configuration
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
* category choices
* source file handling
* source file movement after initial save
* source temp file cleanup
* local thumbnail field behavior
* generated thumbnail path handling
* HLS processing
* FFmpeg command generation
* video duration detection with ffprobe
* dynamic thumbnail timestamp selection
* thumbnail generation with FFmpeg
* processing status changes
* processing error handling
* cleanup after failed conversions
* source file cleanup after failed processing
* thumbnail cleanup after failed processing
* complete media directory cleanup after video deletion
* automatic conversion job scheduling after database commit
* prevention of duplicate conversion jobs on metadata updates
* Django admin configuration
* readonly processing status and error fields
* generated thumbnail preview in the admin
* removal of manual HLS conversion and retry actions
* Django RQ task behavior
* Redis-backed video list caching
* cache invalidation
* authenticated video list access
* video list serialization
* absolute thumbnail URL serialization
* ready-video filtering
* creation-date ordering
* HLS manifest delivery
* HLS segment delivery
* supported resolution validation
* missing file handling
* unauthorized access handling
* internal error handling

Tests use isolated temporary media directories where file-system operations are required.

External processes and integrations such as FFmpeg, ffprobe, Django RQ, Redis and email delivery are mocked where appropriate.

The complete workflow was additionally verified manually through the Django admin and the compatible frontend, including real HLS conversion, generated thumbnail delivery, account activation, login, password reset, video list loading and HLS video playback.

A long-video conversion was verified with `Big_Buck_Bunny_medium.ogv`, including asynchronous worker processing and successful frontend playback after conversion.

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
    ├── test_video_auto_processing.py
    ├── test_video_cache.py
    ├── test_video_list_api.py
    ├── test_video_manifest_api.py
    ├── test_video_model.py
    ├── test_video_segment_api.py
    └── test_video_tasks.py
```

Run all tests:

```bash
docker-compose exec web python -m pytest
```

Run all tests with verbose output:

```bash
docker-compose exec web python -m pytest -v
```

Run all authentication tests:

```bash
docker-compose exec web python -m pytest auth_app/tests/
```

Run all video tests:

```bash
docker-compose exec web python -m pytest videos_app/tests/
```

Run a single authentication test file:

```bash
docker-compose exec web python -m pytest auth_app/tests/test_registration_api.py
```

Run a single video test file:

```bash
docker-compose exec web python -m pytest videos_app/tests/test_video_list_api.py
```

Run the automatic video processing tests:

```bash
docker-compose exec web python -m pytest videos_app/tests/test_video_auto_processing.py
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

Restart the Django RQ worker container:

```bash
docker-compose restart worker
```

Restart both backend and worker containers:

```bash
docker-compose restart web worker
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

Follow the Django RQ worker logs:

```bash
docker-compose logs -f worker
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
