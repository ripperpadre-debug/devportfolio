from django.urls import path
from . import views
from . import dashboard_views as dv

urlpatterns = [
    # Public site
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('share/<int:post_id>/', views.share_to_social, name='share_to_social'),

    # Dashboard auth
    path('dashboard/login/', dv.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', dv.dashboard_logout, name='dashboard_logout'),

    # Dashboard pages
    path('dashboard/', dv.dashboard_home, name='dashboard_home'),
    path('dashboard/profile/', dv.dashboard_profile, name='dashboard_profile'),

    path('dashboard/projects/', dv.dashboard_projects, name='dashboard_projects'),
    path('dashboard/projects/add/', dv.dashboard_project_add, name='dashboard_project_add'),
    path('dashboard/projects/<int:pk>/edit/', dv.dashboard_project_edit, name='dashboard_project_edit'),
    path('dashboard/projects/<int:pk>/delete/', dv.dashboard_project_delete, name='dashboard_project_delete'),

    path('dashboard/skills/', dv.dashboard_skills, name='dashboard_skills'),
    path('dashboard/skills/add/', dv.dashboard_skill_add, name='dashboard_skill_add'),
    path('dashboard/skills/<int:pk>/edit/', dv.dashboard_skill_edit, name='dashboard_skill_edit'),
    path('dashboard/skills/<int:pk>/delete/', dv.dashboard_skill_delete, name='dashboard_skill_delete'),

    path('dashboard/blog/', dv.dashboard_blog, name='dashboard_blog'),
    path('dashboard/blog/add/', dv.dashboard_post_add, name='dashboard_post_add'),
    path('dashboard/blog/<int:pk>/edit/', dv.dashboard_post_edit, name='dashboard_post_edit'),
    path('dashboard/blog/<int:pk>/delete/', dv.dashboard_post_delete, name='dashboard_post_delete'),
    path('dashboard/blog/<int:pk>/toggle/', dv.dashboard_post_toggle, name='dashboard_post_toggle'),

    path('dashboard/messages/', dv.dashboard_messages, name='dashboard_messages'),
    path('dashboard/messages/<int:pk>/', dv.dashboard_message_view, name='dashboard_message_view'),
    path('dashboard/messages/<int:pk>/delete/', dv.dashboard_message_delete, name='dashboard_message_delete'),
]
