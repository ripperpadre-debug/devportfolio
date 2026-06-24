# Django Developer Portfolio

A full-featured portfolio website for software developers, full-stack engineers, and data scientists. Built with Django.

## Features

- **Homepage** — Hero, animated skill bars, featured projects, recent blog posts
- **Projects** — Filterable gallery with category tags, status badges, detail pages
- **Blog** — Tag-filtered articles with social auto-posting to Twitter/X and LinkedIn
- **Contact** — Form that saves messages to the database (readable in Admin)
- **Admin Panel** — Full CMS: manage profile, projects, skills, posts, and messages
- **Social Media Integration** — Publish blog posts to Twitter and LinkedIn with one click

## Quick Start

```bash
# 1. Clone / unzip the project
cd devportfolio

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (optional – for social posting)
cp .env.example .env
# Edit .env with your API keys

# 5. Run migrations
python manage.py migrate

# 6. Load demo data
python manage.py seed_data

# 7. Create admin user
python manage.py createsuperuser

# 8. Run the server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** for the portfolio.
Visit **http://127.0.0.1:8000/admin/** to manage content.

## How to Update Your Portfolio

### Add a Project
1. Go to `/admin/` → Projects → Add Project
2. Fill in title, description, tech stack, images
3. Check "Featured" to show on homepage

### Write a Blog Post
1. Go to `/admin/` → Blog Posts → Add Blog Post
2. Write your content, add tags, set Published = Yes
3. Open the post on your site and click "Share on Twitter/X" or "Share on LinkedIn"

### Update Your Profile
1. Go to `/admin/` → Profiles → Your Profile
2. Update name, bio, social links, avatar, resume

### Add Skills
1. Go to `/admin/` → Skills → Add Skill
2. Set category (Frontend, Backend, Data Science, DevOps)
3. Set proficiency (0-100)

## Social Media Auto-Posting

### Twitter / X
1. Go to [developer.twitter.com](https://developer.twitter.com) and create an app
2. Get API Key, API Secret, Access Token, Access Token Secret
3. Add them to your `.env` file
4. Install tweepy: `pip install tweepy`

### LinkedIn
1. Go to [linkedin.com/developers](https://linkedin.com/developers) and create an app
2. Get an access token with `w_member_social` permission
3. Find your Person ID via the LinkedIn API
4. Add both to your `.env` file

## Customization

- **Colors**: Edit CSS variables in `core/templates/core/base.html` (`:root` block)
- **Fonts**: Change Google Fonts import in `base.html`
- **Layout**: All templates are in `core/templates/core/`

## Deployment (Render / Railway / VPS)

```bash
# Production settings to add to .env
DEBUG=False
SECRET_KEY=strong-random-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Collect static files
python manage.py collectstatic

# Use gunicorn in production
pip install gunicorn
gunicorn portfolio.wsgi:application
```

## Admin Login

Username: `admin`
Password: `admin123` ← **Change this immediately!**

---
Built with Django | © 2025
