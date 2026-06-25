from django.contrib import admin
from .models import Profile, Project, BlogPost, Skill, ContactMessage, SocialShareLog, LegalPage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'tagline', 'location', 'email']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'order']
    list_editable = ['proficiency', 'order']
    list_filter = ['category']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'featured', 'created_at']
    list_editable = ['featured', 'status']
    list_filter = ['category', 'status', 'featured']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published', 'shared_to_twitter', 'shared_to_linkedin', 'created_at']
    list_editable = ['published']
    list_filter = ['published', 'shared_to_twitter', 'shared_to_linkedin']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'sent_at', 'read']
    list_editable = ['read']
    list_filter = ['read']


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ['page_type', 'title', 'updated_at']
    readonly_fields = ['page_type', 'updated_at']


@admin.register(SocialShareLog)
class SocialShareLogAdmin(admin.ModelAdmin):
    list_display = ['platform', 'post', 'status', 'shared_at']
    list_filter = ['platform', 'status']
