# Flexible Web Checker - AI Agents Guide

## 🎯 Agent Execution Principles

### Context Gathering Strategy

**Goal**: Get enough context fast. Parallelize discovery and stop as soon as you can act.

**Method**:

- Start broad, then fan out to focused subqueries
- In parallel, launch varied queries; read top hits per query
- Deduplicate paths and cache; don't repeat queries
- Avoid over-searching for context

**Early Stop Criteria**:

- You can name exact content to change
- Top hits converge (~70%) on one area/path

**Escalate Once**:

- If signals conflict or scope is fuzzy, run one refined parallel batch, then proceed

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

---

## 📋 Project Overview

Django 5.2 + Celery web application monitoring URL changes (RSS/HTML/custom selectors) with multi-language support (ja/en).

---

## 🏗️ Architecture

### Backend Stack

- **Framework**: Django 5.2 (Python 3.12+), single app `bookmark/`
- **Async Tasks**: Celery + Redis/memory broker
- **Scheduling**: django-celery-beat with DatabaseScheduler
- **Soft Deletes**: django-safedelete
- **Database**: SQLite (dev), configurable via `.env`
- **Custom User**: Email-based auth (`bookmark.User`)

### Frontend Stack

- **Build**: Gulp + Parcel (TS/JS), Tailwind CLI (CSS)
- **Languages**: TypeScript 5, React 19, SCSS 1.69.7
- **Styling**: Tailwind CSS 4 (scans `bookmark/templates/**/*.html`, `bookmark/forms/**/*.py`)
- **UI Libraries**: SweetAlert2, Font Awesome 6, CKEditor5
- **Package Manager**: Yarn (preferred), npm compatible

### Module Organization

```text
bookmark/
├── models/      # user, url_item, collection, notification
├── views/       # core, url_manager, collection_manager, user_accounts, i18n
├── forms/       # url_manager, collection_manager, user_accounts
├── tasks/       # url_check, thumbnail (Celery tasks)
└── utils/       # url_check (core checking logic)
```

---

## ⚡ Critical Workflows

### 1. Model Changes (ALWAYS VERIFY)

```bash
# After editing any model file, ALWAYS run:
python manage.py makemigrations bookmark  # Verify changes detected
python manage.py migrate                   # Apply to database
```

### 2. Frontend Build Pipeline

```bash
# Complete setup (sequential order):
yarn install
yarn build:ts          # TypeScript → static/js/
yarn build:js          # JavaScript → static/js/
yarn build:css:prod    # Tailwind → static/css/theme.css (minified)
yarn build:scss        # SCSS → static/css/app.css + app.min.css
yarn setup:libs        # Copy JS libs to static/assets/libs/
yarn setup:fa          # Copy FontAwesome to static/assets/fonts/

# Development watch mode:
yarn watch:css         # Auto-rebuild on template changes
```

### 3. Running Background Tasks (3 Terminals Required)

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A flexible_web_checker worker -l info

# Terminal 3: Celery Beat (scheduler)
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 4. Internationalization (i18n)

```bash
# 1. Mark strings: {% trans %} (templates) or gettext_lazy() (Python)
# 2. Extract messages
python manage.py makemessages -l ja
python manage.py makemessages -l en

# 3. Edit locale/{ja,en}/LC_MESSAGES/django.po files
# 4. Compile (REQUIRED for changes to appear)
python manage.py compilemessages

# Quality checks (run before committing):
python scripts/check_lang_diff.py              # Missing translations
python scripts/check_lang_duplicates_msgid.py  # Duplicate msgids
python scripts/sort_po_by_msgid.py             # Alphabetical sort
```

**Language Middleware**: `bookmark.middleware.LanguageMiddleware` - Cookie → Browser lang → Japanese fallback

---

## 🎨 Code Conventions

### Guiding Principles

1. **Readability**: Avoid environment-dependent characters, emojis, or non-standard character strings in code/comments
2. **Maintainability**: Follow proper directory structure, consistent naming conventions, organize shared logic appropriately
3. **Consistency**: UI must adhere to unified design system—color tokens, typography, spacing, and components
4. **Visual Quality**: Follow high visual quality bar (spacing, padding, hover states, etc.)

### Style Guidelines

- **Python**: Black (line-length=160), Pylint with Django plugin (`pyproject.toml`)
- **TypeScript/JS**: ESLint + Prettier (`package.json`)
- **Comments**: Strictly avoid environment-dependent chars, emojis (readability principle)
- **UI Components**: Maintain consistent design tokens across all components

### URL Checking System (Core Feature)

3 check types in `bookmark/models/url_item.py`:

1. **RSS**: Parse feed, hash combined entry titles/links
2. **HTML_STANDARD**: Hash entire `<body>` content
3. **HTML_CUSTOM**: Monitor CSS selectors with OR/AND conditions

Implementation: `bookmark/utils/url_check.py` (requests + BeautifulSoup4 + Playwright)

### Environment Configuration

Use `django-environ`: Copy `.env.example` → `.env`

- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `CELERY_BROKER_URL` (default: `memory://`)
- Email settings (`EMAIL_HOST`, `EMAIL_PORT`, etc.)
- `UPDATE_CHECK_SCHEDULE` (cron expression)

### Template & Static Files

- **Base**: `bookmark/templates/layouts/base.html`
- **Structure**: `core/`, `url_manager/`, `collection_manager/`, `user_accounts/`, `registration/`
- **Styling**: Tailwind utilities + custom SCSS (`frontend/scss/app.scss`)
- **Dev**: `static/` (STATICFILES_DIRS)
- **Prod**: `python manage.py collectstatic` → `staticfiles/` (ManifestStaticFilesStorage)

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `bookmark/tasks/url_check.py` | Celery tasks for scheduled URL checks |
| `bookmark/utils/url_check.py` | Core checking logic (RSS/HTML parsing) |
| `flexible_web_checker/settings.py` | Django config (lines 200-298: Celery/email/app) |
| `gulpfile.js` | Frontend build orchestration |
| `tailwind.config.js` | Tailwind content paths |
| `Documents/テーブル定義.md` | Database schema reference |

---

## 🧪 Testing & Quality

```bash
# Run tests
python manage.py test bookmark

# Check migrations (dry-run)
python manage.py makemigrations --check --dry-run

# Lint Python
pylint bookmark/  # Config in pyproject.toml

# Translation validation
python scripts/check_lang_diff.py
python scripts/check_lang_duplicates_msgid.py
python scripts/sort_po_by_msgid.py
```

---

## ⚠️ Common Pitfalls & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Celery workers not running** | URL checks don't execute | Start workers in 3 terminals (see above) |
| **Missing `compilemessages`** | Translations don't display | Run `python manage.py compilemessages` |
| **Skipped TypeScript build** | Frontend interactions fail | Run `yarn build:ts` |
| **Wrong Python environment** | Import errors, wrong versions | Activate venv: `source venv/bin/activate` |
| **Editing .mo files directly** | Changes lost on recompile | Always edit .po files, then recompile |
| **Tailwind classes not applied** | Styling missing | Run `yarn watch:css` or `yarn build:css:prod` |
| **Migration not detected** | Model changes ignored | Always run `makemigrations bookmark` after edits |

---

## 🚀 Quick Start for Agents

### Initial Setup

```bash
# 1. Setup environment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed

# 2. Build frontend
yarn install
yarn build:ts && yarn build:js && yarn build:css:prod && yarn build:scss
yarn setup:libs && yarn setup:fa

# 3. Initialize database
python manage.py compilemessages
python manage.py migrate
python manage.py createsuperuser

# 4. Run (3 terminals)
python manage.py runserver  # Terminal 1
celery -A flexible_web_checker worker -l info  # Terminal 2
celery -A flexible_web_checker beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler  # Terminal 3
```

### Development Workflow

1. **Model changes** → `makemigrations bookmark` → `migrate`
2. **Template/form changes** → Tailwind watch mode (`yarn watch:css`)
3. **Translation changes** → Edit `.po` → `compilemessages`
4. **TypeScript/React changes** → `yarn build:ts`
5. **Test** → `python manage.py test bookmark`

---

## 🤖 Agent Execution Best Practices

### Task Decomposition

When receiving a complex task:

1. **Understand Requirements**: Parse the user's request for main objectives and constraints
2. **Identify Dependencies**: Map out which components depend on others
3. **Prioritize Actions**: Order tasks by dependency chain (models → migrations → views → templates → frontend)
4. **Execute Incrementally**: Complete one unit, validate, then proceed to next

### Context Discovery Pattern

```text
1. Initial Reconnaissance (Parallel)
   ├─ semantic_search: "feature X implementation"
   ├─ grep_search: "class FeatureX|def feature_x"
   └─ file_search: "**/*feature*.py"

2. Convergence Check
   └─ If 70%+ results point to same files → Read those files
   └─ If scattered → Run one refined parallel batch

3. Deep Dive (Sequential)
   └─ read_file: Read identified files with sufficient context (50-100 lines)
   └─ list_code_usages: Trace symbols you'll modify

4. Act
   └─ Make changes with full context
```

### Common Agent Workflows

#### Adding a New Model Field

```text
1. grep_search: Find model definition
2. read_file: Read model + related forms/views
3. Edit model → makemigrations → migrate
4. Update forms/views/templates
5. Update translations if needed
6. Run tests
```

#### Fixing a Bug

```text
1. semantic_search: Find relevant code by symptom description
2. Read top 3-5 files returned
3. list_code_usages: Trace function/class causing issue
4. Identify root cause
5. Fix + add test case if missing
6. Validate with runTests
```

#### Implementing New Feature

```text
1. Search existing similar features (semantic_search)
2. Read models → Identify data requirements
3. Create/modify models → makemigrations → migrate
4. Create forms/views following existing patterns
5. Create templates using Tailwind + existing components
6. Add translations (ja/en)
7. Update frontend (TypeScript/React) if needed → build
8. Run tests
```

### Quality Assurance Checklist

Before completing a task, verify:

- [ ] Migrations created and applied (if models changed)
- [ ] Frontend rebuilt (if TS/JS/CSS changed)
- [ ] Translations added (ja/en) and compiled
- [ ] Code follows project style (Black, ESLint)
- [ ] No hardcoded strings in UI (use {% trans %})
- [ ] Tests pass (`python manage.py test bookmark`)
- [ ] No linting errors
- [ ] Documentation updated if needed

### Error Recovery Strategies

| Error Type | Detection | Recovery |
|------------|-----------|----------|
| **Import Error** | `ModuleNotFoundError` | Check venv activated, run `pip install -r requirements.txt` |
| **Migration Conflict** | `Conflicting migrations` | Check migration history, resolve conflicts, recreate migration |
| **Translation Missing** | String not translated in UI | Run `makemessages`, edit .po, run `compilemessages` |
| **Frontend Build Fail** | Parcel/Tailwind error | Check syntax errors, node_modules integrity, rerun build |
| **Celery Task Not Running** | Task queued but not executed | Verify worker/beat processes running in separate terminals |
| **Template Syntax Error** | `TemplateSyntaxError` | Check Django template tags syntax, ensure {% load %} present |

---

## 📚 Additional Resources

- **README.md**: Detailed setup instructions
- **Documents/テーブル定義.md**: Database schema
- **Documents/setup_apache_*.md**: Production deployment
- **.cursor/rules/global.mdc**: Additional coding guidelines
