from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import Profile, Project, Skill, BlogPost, ContactMessage
from .forms import ProfileForm, ProjectForm, SkillForm, BlogPostForm


def _staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/dashboard/login/?next={request.path}')
        if not request.user.is_staff:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def _dash_context(request, **extra):
    unread = ContactMessage.objects.filter(read=False).count()
    ctx = {'unread_count': unread}
    ctx.update(extra)
    return ctx


# ── AUTH ───────────────────────────────────────────────────────────

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard_home')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            unread = ContactMessage.objects.filter(read=False).count()
            if unread:
                messages.success(request, f'👋 Welcome back! You have {unread} unread message{"s" if unread != 1 else ""}.')
            else:
                messages.success(request, f'👋 Welcome back, {user.username}!')
            return redirect(request.GET.get('next', '/dashboard/'))
        error = 'Invalid username or password.'
    return render(request, 'core/dashboard/login.html', {'error': error})


def dashboard_logout(request):
    logout(request)
    return redirect('/')


# ── HOME ────────────────────────────────────────────────────────────

@_staff_required
def dashboard_home(request):
    ctx = _dash_context(request,
        project_count=Project.objects.count(),
        post_count=BlogPost.objects.filter(published=True).count(),
        draft_count=BlogPost.objects.filter(published=False).count(),
        skill_count=Skill.objects.count(),
        message_count=ContactMessage.objects.filter(read=False).count(),
        recent_messages=ContactMessage.objects.order_by('-sent_at')[:5],
        recent_posts=BlogPost.objects.order_by('-updated_at')[:5],
        recent_projects=Project.objects.order_by('-updated_at')[:5],
    )
    return render(request, 'core/dashboard/home.html', ctx)


# ── PROFILE ─────────────────────────────────────────────────────────

@_staff_required
def dashboard_profile(request):
    profile = Profile.objects.first()
    if profile is None:
        profile = Profile.objects.create()
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('dashboard_profile')
    ctx = _dash_context(request, form=form, profile=profile)
    return render(request, 'core/dashboard/profile.html', ctx)


# ── PROJECTS ────────────────────────────────────────────────────────

@_staff_required
def dashboard_projects(request):
    all_projects = Project.objects.all()
    paginator = Paginator(all_projects, 15)
    page = request.GET.get('page')
    projects = paginator.get_page(page)
    ctx = _dash_context(request, projects=projects)
    return render(request, 'core/dashboard/projects.html', ctx)


@_staff_required
def dashboard_project_add(request):
    form = ProjectForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        if not project.slug:
            project.slug = slugify(project.title)
        base_slug = project.slug
        counter = 1
        while Project.objects.filter(slug=project.slug).exists():
            project.slug = f'{base_slug}-{counter}'
            counter += 1
        project.save()
        messages.success(request, f'Project "{project.title}" created.')
        return redirect('dashboard_projects')
    ctx = _dash_context(request, form=form, action='Add', project=None)
    return render(request, 'core/dashboard/project_form.html', ctx)


@_staff_required
def dashboard_project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = ProjectForm(request.POST or None, request.FILES or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Project "{project.title}" updated.')
        return redirect('dashboard_projects')
    ctx = _dash_context(request, form=form, action='Edit', project=project)
    return render(request, 'core/dashboard/project_form.html', ctx)


@_staff_required
@require_POST
def dashboard_project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    name = project.title
    project.delete()
    messages.success(request, f'Project "{name}" deleted.')
    return redirect('dashboard_projects')


# ── SKILLS ──────────────────────────────────────────────────────────

@_staff_required
def dashboard_skills(request):
    all_skills = Skill.objects.all()
    paginator = Paginator(all_skills, 20)
    page = request.GET.get('page')
    skills = paginator.get_page(page)
    ctx = _dash_context(request, skills=skills)
    return render(request, 'core/dashboard/skills.html', ctx)


@_staff_required
def dashboard_skill_add(request):
    form = SkillForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Skill added.')
        return redirect('dashboard_skills')
    ctx = _dash_context(request, form=form, action='Add', skill=None)
    return render(request, 'core/dashboard/skill_form.html', ctx)


@_staff_required
def dashboard_skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    form = SkillForm(request.POST or None, instance=skill)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Skill "{skill.name}" updated.')
        return redirect('dashboard_skills')
    ctx = _dash_context(request, form=form, action='Edit', skill=skill)
    return render(request, 'core/dashboard/skill_form.html', ctx)


@_staff_required
@require_POST
def dashboard_skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    name = skill.name
    skill.delete()
    messages.success(request, f'Skill "{name}" deleted.')
    return redirect('dashboard_skills')


# ── BLOG ────────────────────────────────────────────────────────────

@_staff_required
def dashboard_blog(request):
    all_posts = BlogPost.objects.all()
    paginator = Paginator(all_posts, 15)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    ctx = _dash_context(request, posts=posts)
    return render(request, 'core/dashboard/blog.html', ctx)


@_staff_required
def dashboard_post_add(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        if not post.slug:
            post.slug = slugify(post.title)
        base_slug = post.slug
        counter = 1
        while BlogPost.objects.filter(slug=post.slug).exists():
            post.slug = f'{base_slug}-{counter}'
            counter += 1
        post.save()
        messages.success(request, f'Post "{post.title}" created.')
        return redirect('dashboard_blog')
    ctx = _dash_context(request, form=form, action='Add', post=None)
    return render(request, 'core/dashboard/post_form.html', ctx)


@_staff_required
def dashboard_post_edit(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    form = BlogPostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Post "{post.title}" updated.')
        return redirect('dashboard_blog')
    ctx = _dash_context(request, form=form, action='Edit', post=post)
    return render(request, 'core/dashboard/post_form.html', ctx)


@_staff_required
@require_POST
def dashboard_post_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    name = post.title
    post.delete()
    messages.success(request, f'Post "{name}" deleted.')
    return redirect('dashboard_blog')


@_staff_required
def dashboard_post_toggle(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    post.published = not post.published
    post.save()
    status = 'published' if post.published else 'unpublished'
    messages.success(request, f'"{post.title}" {status}.')
    return redirect('dashboard_blog')


# ── MESSAGES ────────────────────────────────────────────────────────

@_staff_required
def dashboard_messages(request):
    all_msgs = ContactMessage.objects.all()
    paginator = Paginator(all_msgs, 15)
    page = request.GET.get('page')
    msgs = paginator.get_page(page)
    ctx = _dash_context(request, contact_messages=msgs)
    return render(request, 'core/dashboard/messages.html', ctx)


@_staff_required
def dashboard_message_view(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.read:
        msg.read = True
        msg.save()
    ctx = _dash_context(request, msg=msg)
    return render(request, 'core/dashboard/message_view.html', ctx)


@_staff_required
@require_POST
def dashboard_message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, 'Message deleted.')
    return redirect('dashboard_messages')
