import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from .models import Profile, Project, BlogPost, Skill, ContactMessage, SocialShareLog, LegalPage


def get_profile():
    return Profile.objects.first()


def home(request):
    profile = get_profile()
    featured_projects = Project.objects.filter(featured=True)[:3]
    all_projects = Project.objects.all()[:6]
    skills = Skill.objects.all()
    recent_posts = BlogPost.objects.filter(published=True)[:3]
    skill_categories = {}
    for skill in skills:
        cat = skill.get_category_display()
        skill_categories.setdefault(cat, []).append(skill)
    context = {
        'profile': profile,
        'featured_projects': featured_projects,
        'all_projects': all_projects,
        'skill_categories': skill_categories,
        'recent_posts': recent_posts,
    }
    return render(request, 'core/home.html', context)


def projects(request):
    category = request.GET.get('category', '')
    qs = Project.objects.all()
    if category:
        qs = qs.filter(category=category)
    paginator = Paginator(qs, 9)
    page = request.GET.get('page')
    projects_page = paginator.get_page(page)
    categories = Project.CATEGORY_CHOICES
    context = {'projects': projects_page, 'categories': categories, 'active_category': category}
    return render(request, 'core/projects.html', context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    related = Project.objects.filter(category=project.category).exclude(pk=project.pk)[:3]
    return render(request, 'core/project_detail.html', {'project': project, 'related': related})


def blog(request):
    tag = request.GET.get('tag', '')
    posts = BlogPost.objects.filter(published=True)
    if tag:
        posts = [p for p in posts if tag.lower() in [t.lower() for t in p.get_tags_list()]]
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    all_tags = set()
    for p in BlogPost.objects.filter(published=True):
        all_tags.update(p.get_tags_list())
    return render(request, 'core/blog.html', {'posts': posts_page, 'all_tags': sorted(all_tags), 'active_tag': tag})


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    related = BlogPost.objects.filter(published=True).exclude(pk=post.pk)[:3]
    return render(request, 'core/blog_detail.html', {'post': post, 'related': related})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            # Email notification
            try:
                notify_email = getattr(settings, 'NOTIFY_EMAIL', '')
                if notify_email:
                    send_mail(
                        subject=f"📬 New contact: {subject or '(no subject)'} — from {name}",
                        message=(
                            f"You have a new message on your portfolio!\n\n"
                            f"From:    {name}\n"
                            f"Email:   {email}\n"
                            f"Subject: {subject or '(none)'}\n\n"
                            f"Message:\n{message}\n\n"
                            f"---\nReply directly to: {email}\n"
                            f"View in dashboard: /dashboard/messages/"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[notify_email],
                        fail_silently=True,
                    )
            except Exception:
                pass
            messages.success(request, "Message sent! I'll get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all required fields.")
    return render(request, 'core/contact.html', {'profile': get_profile()})


@staff_member_required
@require_POST
def share_to_social(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    platform = request.POST.get('platform')
    site_url = request.build_absolute_uri('/')
    post_url = f"{site_url}blog/{post.slug}/"
    result = {'success': False, 'message': ''}

    if platform == 'twitter':
        result = _share_twitter(post, post_url)
        if result['success']:
            post.shared_to_twitter = True
            post.save()
    elif platform == 'linkedin':
        result = _share_linkedin(post, post_url)
        if result['success']:
            post.shared_to_linkedin = True
            post.save()

    SocialShareLog.objects.create(
        platform=platform, post=post,
        status='success' if result['success'] else 'failed',
        response_data=result.get('message', '')
    )
    return JsonResponse(result)


def _share_twitter(post, url):
    token = settings.TWITTER_ACCESS_TOKEN
    token_secret = settings.TWITTER_ACCESS_SECRET
    api_key = settings.TWITTER_API_KEY
    api_secret = settings.TWITTER_API_SECRET
    if not all([token, token_secret, api_key, api_secret]):
        return {'success': False, 'message': 'Twitter credentials not configured. Add them to your .env file.'}
    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key, consumer_secret=api_secret,
            access_token=token, access_token_secret=token_secret
        )
        tags = ' '.join([f'#{t.replace(" ", "")}' for t in post.get_tags_list()[:3]])
        tweet_text = f"{post.title}\n\n{post.excerpt[:150] if post.excerpt else ''}\n\n{url}\n\n{tags}"
        response = client.create_tweet(text=tweet_text[:280])
        return {'success': True, 'message': f'Tweeted! ID: {response.data["id"]}'}
    except ImportError:
        return {'success': False, 'message': 'Install tweepy: pip install tweepy'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _share_linkedin(post, url):
    token = settings.LINKEDIN_ACCESS_TOKEN
    person_id = settings.LINKEDIN_PERSON_ID
    if not token or not person_id:
        return {'success': False, 'message': 'LinkedIn credentials not configured. Add them to your .env file.'}
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        text = f"{post.title}\n\n{post.excerpt}\n\nRead more: {url}"
        payload = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "ARTICLE",
                    "media": [{"status": "READY", "originalUrl": url}]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        r = requests.post('https://api.linkedin.com/v2/ugcPosts', headers=headers, json=payload)
        if r.status_code in (200, 201):
            return {'success': True, 'message': 'Posted to LinkedIn!'}
        return {'success': False, 'message': r.text}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def terms(request):
    page = LegalPage.objects.filter(page_type='terms').first()
    return render(request, 'core/legal.html', {'page': page, 'page_name': 'Terms of Service'})


def privacy(request):
    page = LegalPage.objects.filter(page_type='privacy').first()
    return render(request, 'core/legal.html', {'page': page, 'page_name': 'Privacy Policy'})


def sitemap(request):
    pages = [
        {'loc': '/', 'changefreq': 'weekly', 'priority': '1.0'},
        {'loc': '/projects/', 'changefreq': 'weekly', 'priority': '0.9'},
        {'loc': '/blog/', 'changefreq': 'weekly', 'priority': '0.8'},
        {'loc': '/contact/', 'changefreq': 'monthly', 'priority': '0.7'},
        {'loc': '/terms/', 'changefreq': 'monthly', 'priority': '0.3'},
        {'loc': '/privacy/', 'changefreq': 'monthly', 'priority': '0.3'},
    ]
    from .models import Project, BlogPost
    for project in Project.objects.all():
        pages.append({'loc': f'/projects/{project.slug}/', 'changefreq': 'monthly', 'priority': '0.7', 'lastmod': project.updated_at})
    for post in BlogPost.objects.filter(published=True):
        pages.append({'loc': f'/blog/{post.slug}/', 'changefreq': 'monthly', 'priority': '0.7', 'lastmod': post.updated_at})

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{request.scheme}://{request.get_host()}{p["loc"]}</loc>\n'
        xml += f'    <changefreq>{p["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{p["priority"]}</priority>\n'
        if 'lastmod' in p:
            xml += f'    <lastmod>{p["lastmod"].strftime("%Y-%m-%d")}</lastmod>\n'
        xml += '  </url>\n'
    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml')


def page_not_found(request, exception):
    return render(request, 'core/404.html', status=404)

def server_error(request):
    return render(request, 'core/500.html', status=500)

def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)

def bad_request(request, exception):
    return render(request, 'core/400.html', status=400)

def robots(request):
    lines = [
        'User-agent: *',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        '',
        f'Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
