````instructions
# Flexible Web Checker - AI Coding Agent Instructions

## Agent Execution Principles

### Context Gathering Strategy

**Goal**: Get enough context fast. Parallelize discovery and stop as soon as you can act.

**Method**:
- Start broad, then fan out to focused subqueries
- Launch varied queries in parallel; read top hits per query
- Deduplicate paths and cache; don't repeat queries
- Avoid over-searching for context

**Early Stop Criteria**:
- You can name exact content to change
- Top hits converge (~70%) on one area/path

**Depth Control**:
- Trace only symbols you'll modify or whose contracts you rely on
- Avoid transitive expansion unless necessary

**Loop**: Batch search → minimal plan → complete task. Search again only if validation fails.

### Self-Reflection Process

Before implementing solutions:
1. **Create Internal Rubric**: Develop 5-7 categories defining world-class solutions (don't show to user)
2. **Deep Thinking**: Consider every aspect against this rubric
3. **Iterate Internally**: If not hitting top marks across all categories, redesign
4. **Only Then Implement**: Proceed when confident in the approach

### Persistence & Autonomy

- **Keep going** until the task is completely resolved
- **Never stop** when encountering uncertainty—research or deduce the most reasonable approach
- **Don't ask for confirmation** on assumptions—proceed and document decisions afterward
- **Only terminate** when you're certain the problem is solved

## Project Overview

A Django 5.2 + Celery web application that monitors URL changes (RSS feeds, HTML content, custom selectors) and notifies users of updates. Users organize URLs into collections with multi-language support (ja/en).

## Architecture

### Backend Stack
- **Framework**: Django 5.2 (Python 3.12+) with single app structure (`bookmark/`)
- **Async Tasks**: Celery + Redis/memory broker for background URL checking
- **Task Scheduling**: django-celery-beat with DatabaseScheduler
- **Soft Deletes**: django-safedelete plugin
- **Database**: SQLite (dev), configurable via `.env`

### Frontend Stack
- **Build System**: Gulp + Parcel for TypeScript/JavaScript, Tailwind CLI for CSS
- **Languages**: TypeScript 5, React 19, SCSS 1.69.7
- **Styling**: Tailwind CSS 4 (scans `bookmark/templates/**/*.html` and `bookmark/forms/**/*.py`)
- **Libraries**: SweetAlert2 (dialogs), Font Awesome 6 (icons), CKEditor5 (HTML editing)
- **Package Manager**: Yarn preferred, npm compatible

### Module Organization
- **Models**: Split into `bookmark/models/{user,url_item,collection,notification}.py` (imported via `__init__.py`)
- **Views**: `bookmark/views/{core,url_manager,collection_manager,user_accounts,i18n}.py`
- **Forms**: `bookmark/forms/{url_manager,collection_manager,user_accounts}.py`
- **Tasks**: `bookmark/tasks/{url_check,thumbnail}.py` - Celery tasks for async operations
- **Utils**: `bookmark/utils/url_check.py` - Core URL checking logic (RSS, HTML standard/custom)

## Critical Workflows

### Model Changes
**Always run `python manage.py makemigrations bookmark` after editing models** to verify changes are detected. Create migrations explicitly:
```bash
python manage.py makemigrations bookmark
python manage.py migrate
```

### Frontend Build Pipeline
```bash
# Complete setup (run in order)
yarn install
yarn build:ts          # TypeScript → static/js/ (Parcel)
yarn build:js          # JavaScript → static/js/ (Parcel)
yarn build:css:prod    # Tailwind → static/css/theme.css (minified)
yarn build:scss        # SCSS → static/css/app.css + app.min.css
yarn setup:libs        # Copy JS libs to static/assets/libs/
yarn setup:fa          # Copy FontAwesome fonts to static/assets/fonts/

# Development
yarn watch:css         # Auto-rebuild Tailwind on template changes
```

### Running Background Tasks
Open **3 separate terminals**:
```bash
# Terminal 1: Django dev server
python manage.py runserver

# Terminal 2: Celery worker
celery -A flexible_web_checker worker -l info

# Terminal 3: Celery Beat (scheduled tasks)
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Internationalization (i18n)
Supports Japanese (default) and English via Django's translation system.

**Translation Workflow:**
```bash
# 1. Mark strings with {% trans %} in templates or gettext_lazy() in Python
# 2. Extract messages
python manage.py makemessages -l ja
python manage.py makemessages -l en

# 3. Edit locale/{ja,en}/LC_MESSAGES/django.po files
# 4. Compile
python manage.py compilemessages

# Quality checks (run before committing)
python scripts/check_lang_diff.py              # Find missing translations
python scripts/check_lang_duplicates_msgid.py  # Detect duplicate msgids
python scripts/sort_po_by_msgid.py             # Sort .po files alphabetically
```

**Custom Language Middleware**: `bookmark.middleware.LanguageMiddleware` reads language from cookies, falls back to browser preference, defaults to Japanese for unsupported languages.

## Project-Specific Conventions

### Guiding Principles

1. **Readability**: Avoid environment-dependent characters, emojis, or non-standard character strings in code/comments
2. **Maintainability**: Follow proper directory structure, consistent naming conventions, organize shared logic appropriately
3. **Consistency**: UI must adhere to unified design system—color tokens, typography, spacing, and components
4. **Visual Quality**: Follow high visual quality bar (spacing, padding, hover states, etc.)

### Code Style
- **Python**: Black formatter (line-length=160), Pylint with Django plugin (see `pyproject.toml`)
- **TypeScript/JavaScript**: ESLint with Prettier (configured via package.json)
- **Comments/Docs**: Strictly avoid environment-dependent characters or emojis (readability principle)
- **UI Components**: Maintain consistent design tokens across all components

### URL Checking System
The core feature has 3 check types (see `bookmark/models/url_item.py`):
1. **RSS**: Parses feed, hashes combined entry titles/links
2. **HTML_STANDARD**: Hashes entire `<body>` content
3. **HTML_CUSTOM**: Monitors specific CSS selectors with OR/AND conditions

Implemented in `bookmark/utils/url_check.py` using `requests` + `BeautifulSoup4` + Playwright for screenshots.

### Custom User Model
- `AUTH_USER_MODEL = 'bookmark.User'` (defined in `bookmark/models/user.py`)
- Email-based authentication (no username field)
- Related models: `UserProfile`, `EmailConfirmationToken`, `PasswordResetToken`

### Environment Configuration
All settings use `django-environ`. Copy `.env.example` → `.env` and configure:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `CELERY_BROKER_URL` (default: `memory://`)
- Email settings (`EMAIL_HOST`, `EMAIL_PORT`, etc.)
- `UPDATE_CHECK_SCHEDULE` (cron expression for periodic checks)

### Template Structure
- Base: `bookmark/templates/layouts/base.html`
- Organized by feature: `core/`, `url_manager/`, `collection_manager/`, `user_accounts/`, `registration/`
- Uses Tailwind utility classes + custom SCSS (`frontend/scss/app.scss`)

### Static Files
- Development: `static/` (STATICFILES_DIRS)
- Production: Run `python manage.py collectstatic` → `staticfiles/` (STATIC_ROOT)
- Uses `ManifestStaticFilesStorage` for cache busting

## Key Files/Directories

- **`bookmark/tasks/url_check.py`**: Celery tasks for scheduled URL checks
- **`bookmark/utils/url_check.py`**: Core checking logic (RSS/HTML parsing)
- **`flexible_web_checker/settings.py`**: All Django config (lines 200-298 for Celery/email/app settings)
- **`gulpfile.js`**: Frontend build orchestration (Parcel compilation, lib copying)
- **`tailwind.config.js`**: Tailwind content paths (templates + forms)
- **`Documents/テーブル定義.md`**: Database schema reference

## Testing & Quality
- Run tests: `python manage.py test bookmark`
- Check migrations: `python manage.py makemigrations --check --dry-run`
- Lint Python: `pylint bookmark/` (config in `pyproject.toml`)
- Translation validation: Use scripts in `scripts/` directory before committing

## Common Pitfalls
- **Forgetting to run Celery workers**: URL checks won't execute
- **Missing `compilemessages`**: Translations won't display
- **Skipping TypeScript build**: Frontend interactions will fail
- **Not activating venv**: Wrong Python environment
- **Editing .mo files directly**: Always edit .po files and recompile
