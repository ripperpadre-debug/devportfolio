from django.db import models
from django.utils import timezone


class Profile(models.Model):
    name = models.CharField(max_length=100, default="Your Name")
    tagline = models.CharField(max_length=200, default="Full Stack Developer | Data Scientist")
    bio = models.TextField(default="")
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True)
    resume = models.FileField(upload_to='resume/', blank=True, null=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=100, blank=True, default="Nairobi, Kenya")
    years_experience = models.IntegerField(default=0)
    projects_count = models.IntegerField(default=0)
    clients_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Profile"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('data', 'Data Science'),
        ('devops', 'DevOps & Tools'),
        ('mobile', 'Mobile'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=60)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='backend')
    proficiency = models.IntegerField(default=80, help_text="0-100")
    icon = models.CharField(max_length=100, blank=True, help_text="CSS class or emoji")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Project(models.Model):
    STATUS_CHOICES = [
        ('live', 'Live'),
        ('in_progress', 'In Progress'),
        ('archived', 'Archived'),
    ]
    CATEGORY_CHOICES = [
        ('fullstack', 'Full Stack'),
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('data', 'Data Science / ML'),
        ('mobile', 'Mobile'),
        ('other', 'Other'),
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='fullstack')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='live')
    tech_stack = models.CharField(max_length=500, blank=True, help_text="Comma-separated: Django, React, PostgreSQL")
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return self.title

    def get_tech_list(self):
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()]


class BlogPost(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    excerpt = models.CharField(max_length=400, blank=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags")
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    # Social sharing
    shared_to_twitter = models.BooleanField(default=False)
    shared_to_linkedin = models.BooleanField(default=False)
    twitter_post_id = models.CharField(max_length=100, blank=True)
    linkedin_post_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.name} – {self.subject}"


class SocialShareLog(models.Model):
    PLATFORM_CHOICES = [('twitter', 'Twitter/X'), ('linkedin', 'LinkedIn')]
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='share_logs')
    status = models.CharField(max_length=20, default='pending')
    response_data = models.TextField(blank=True)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.platform} – {self.post.title}"
