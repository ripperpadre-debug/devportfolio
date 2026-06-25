from django import forms
from .models import Profile, Project, Skill, BlogPost, LegalPage


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'tagline', 'bio', 'avatar', 'resume',
            'email', 'location', 'github', 'linkedin', 'twitter',
            'years_experience', 'projects_count', 'clients_count',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'slug', 'tagline', 'description', 'category',
            'status', 'tech_stack', 'image', 'github_url', 'live_url',
            'featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'tagline': forms.TextInput(),
            'tech_stack': forms.TextInput(attrs={'placeholder': 'Django, React, PostgreSQL'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'proficiency', 'icon', 'order']
        widgets = {
            'proficiency': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'excerpt', 'content', 'cover_image',
            'tags', 'published',
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 16}),
            'tags': forms.TextInput(attrs={'placeholder': 'python, django, tutorial'}),
        }


class LegalPageForm(forms.ModelForm):
    class Meta:
        model = LegalPage
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'class': 'field-input code-input'}),
        }
