# Flexible Web Checker

## 1. System Overview

Flexible Web Checker is a Django application that periodically checks specified web pages for updates and notifies users when changes are detected. Users can register URLs and organize them into collections. Update checks are performed asynchronously in the background.

## 2. Development Environment Setup

### 2.1 Prerequisites

- Python 3.12 or higher (Django 5.2)
- gettext (for internationalization)
- Node.js, Yarn

### 2.2 Setup Steps

1. Clone the repository

    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2. Create and activate virtual environment

    ```bash
    # Create virtual environment
    python3 -m venv venv

    # Activate virtual environment
    source venv/bin/activate  # (macOS/Linux)
    .\venv\Scripts\activate  # (Windows)
    ```

3. Install dependencies

    ```bash
    # Install Python dependencies
    pip install -r requirements.txt

    # If gettext is not installed (Ubuntu/Debian)
    # sudo apt-get install gettext
    ```

4. Configure environment variables

    Copy `.env.example` to `.env` and edit as needed

    ```bash
    cp .env.example .env
    # Edit .env file as needed
    ```

5. Install and setup frontend dependencies

    **Note:** This project **recommends using Yarn** as the package manager, but npm also works.
    The following command examples use Yarn. If using npm, please adapt the commands accordingly
    (`yarn install` becomes `npm install`, `yarn <script>` becomes `npm run <script>`).

    ```bash
    # Ensure Node.js and Yarn are installed
    # Install dependencies
    yarn install

    # Build TypeScript
    yarn build:ts

    # Build JavaScript
    yarn build:js

    # Build CSS (Tailwind)
    yarn build:css:prod

    # Build SCSS
    yarn build:scss

    # Copy JavaScript libraries
    yarn setup:libs

    # Copy FontAwesome fonts
    yarn setup:fa

    # Generate icons (if needed)
    # yarn icons

    # Selective module updates
    # yarn upgrade-interactive

    # Update specific module
    # yarn up "sweetalert2"
    ```

6. Compile language files

    ```bash
    # Generate .mo files from .po files
    python manage.py compilemessages
    ```

7. Run database migrations

    ```bash
    python manage.py migrate
    ```

8. Prepare static files (for production, etc.)

    ```bash
    python manage.py collectstatic
    ```

9. Create superuser (administrator account)

    ```bash
    python manage.py createsuperuser
    ```

10. Start development server

    ```bash
    python manage.py runserver
    ```

### 2.3 Verification

Access `http://localhost:8000/` in your browser.

### 2.4 Starting Celery Worker and Beat (for asynchronous tasks)

Launch each in separate terminals.

```bash
# Celery Worker
celery -A flexible_web_checker worker -l info

# Celery Beat (for scheduled tasks)
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## 3. Development Notes

### Models and Migrations

When making changes to Django models (`models.py` or files in the `models/` directory), **migration file creation and application are generally required**.
After editing model files, it is **recommended to habitually run `makemigrations <app-name>`** to verify that either "No changes detected" is displayed or the intended changes are generated as migration files.

1. Running makemigrations
    After making changes to models, run the following command to record the changes in a migration file.

    ```bash
    python manage.py makemigrations bookmark
    ```

    This command detects differences between the model definitions and existing migration files, and generates a new migration file (e.g., `000X_...py`).

2. Running migrate
    Apply the generated migration file to the database with the following command.

    ```bash
    python manage.py migrate
    ```

    This synchronizes the database schema with the model definitions.

### Updating Translation Files (compilemessages)

When manually modifying translation files (`.po` files), or after adding/modifying translatable strings in source code (`{% trans "..." %}`, `trans("...")`, `_("...")`, etc.) and running `python manage.py makemessages -l <language-code>`, you need to compile the translation files with the following command.

```bash
python manage.py compilemessages
```

This generates (or updates) `.mo` files from `.po` files, allowing translations to be correctly reflected in the application's display language.

### Rebuilding CSS (Tailwind CSS)

When adding, modifying, or removing Tailwind CSS utility classes in HTML template files or other files configured as Tailwind CSS scan targets (such as JavaScript or Python files), you need to rebuild the CSS files to reflect the changes.

Many projects provide a watch mode that monitors file changes during development and automatically rebuilds CSS.

```bash
yarn watch:css
# or npm run watch:css
```

Even when using watch mode, it is recommended to periodically run a production build to verify that the final CSS output has no issues.

Production build:

```bash
yarn build:css:prod
# or npm run build:css:prod
```
