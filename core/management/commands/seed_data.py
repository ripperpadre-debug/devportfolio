from django.core.management.base import BaseCommand
from core.models import Profile, Skill, Project, BlogPost


class Command(BaseCommand):
    help = 'Seeds initial demo data'

    def handle(self, *args, **options):
        if not Profile.objects.exists():
            Profile.objects.create(
                name="Alex Kimani",
                tagline="Full Stack Developer | Data Scientist | ML Engineer",
                bio="I'm a passionate software developer based in Nairobi, Kenya. I build scalable web applications, machine learning pipelines, and data-driven products. With expertise in Python, Django, React, and modern ML frameworks, I turn complex problems into elegant solutions.",
                github="https://github.com/yourusername",
                linkedin="https://linkedin.com/in/yourusername",
                twitter="https://twitter.com/yourusername",
                email="hello@example.dev",
                location="Nairobi, Kenya",
                years_experience=4, projects_count=25, clients_count=12,
            )
            self.stdout.write(self.style.SUCCESS('Profile created'))

        skills_data = [
            ('Python','backend',95),('Django','backend',92),('FastAPI','backend',85),
            ('PostgreSQL','backend',88),('REST APIs','backend',92),
            ('React','frontend',85),('JavaScript','frontend',88),('TypeScript','frontend',80),
            ('Tailwind CSS','frontend',90),('HTML/CSS','frontend',95),
            ('TensorFlow','data',82),('Pandas','data',90),('scikit-learn','data',85),
            ('NumPy','data',92),('Matplotlib','data',85),
            ('Docker','devops',80),('Git','devops',95),('AWS','devops',72),
            ('Linux','devops',85),('CI/CD','devops',75),
        ]
        if not Skill.objects.exists():
            for i,(name,cat,prof) in enumerate(skills_data):
                Skill.objects.create(name=name,category=cat,proficiency=prof,order=i)
            self.stdout.write(self.style.SUCCESS(f'{len(skills_data)} skills created'))

        if not Project.objects.exists():
            projects = [
                {'title':'E-Commerce Platform','slug':'ecommerce-platform','tagline':'Full-featured online store with real-time inventory','description':'A complete e-commerce solution built with Django and React. Features include real-time inventory management, payment integration with M-Pesa and Stripe, product recommendations using collaborative filtering, and a responsive admin dashboard.\n\nKey Features:\n- Real-time inventory tracking\n- M-Pesa & Stripe payment integration\n- ML-powered product recommendations\n- Multi-vendor support\n- Analytics dashboard','category':'fullstack','status':'live','tech_stack':'Django, React, PostgreSQL, Redis, Celery, Stripe, M-Pesa','github_url':'https://github.com','live_url':'https://example.com','featured':True},
                {'title':'Crop Disease Detection','slug':'crop-disease-detection','tagline':'CNN model detecting plant diseases from leaf images','description':'A deep learning model that detects crop diseases from leaf photographs with 94% accuracy. Built to help smallholder farmers in Kenya identify plant diseases early.\n\nTrained on 50,000+ images across 38 disease classes using transfer learning on ResNet50. Deployed as a REST API and mobile-friendly web app.','category':'data','status':'live','tech_stack':'Python, TensorFlow, FastAPI, React, PostgreSQL, Docker','github_url':'https://github.com','featured':True},
                {'title':'Real-time Chat App','slug':'realtime-chat-app','tagline':'WebSocket-based chat with end-to-end encryption','description':'A real-time messaging application built with Django Channels and WebSockets. Supports group chats, direct messages, file sharing, and end-to-end encryption with read receipts and typing indicators.','category':'fullstack','status':'live','tech_stack':'Django Channels, WebSocket, React, Redis, PostgreSQL','github_url':'https://github.com','featured':True},
                {'title':'Data Pipeline Dashboard','slug':'data-pipeline-dashboard','tagline':'ETL pipeline with real-time monitoring','description':'An automated ETL pipeline that ingests data from multiple sources, processes it using Apache Spark, and visualizes insights in an interactive dashboard for 2M+ daily transactions.','category':'data','status':'live','tech_stack':'Python, Apache Spark, Airflow, PostgreSQL, React, D3.js','featured':False},
                {'title':'Portfolio CMS','slug':'portfolio-cms','tagline':'This very portfolio — built with Django','description':'A dynamic portfolio website with a built-in CMS, blog engine with social media auto-posting, project management, and contact form.','category':'fullstack','status':'live','tech_stack':'Django, SQLite, Python','github_url':'https://github.com','featured':False},
            ]
            for p in projects:
                Project.objects.create(**p)
            self.stdout.write(self.style.SUCCESS(f'{len(projects)} projects created'))

        if not BlogPost.objects.exists():
            posts = [
                {'title':'Building a Machine Learning Pipeline with Python','slug':'ml-pipeline-python-sklearn','excerpt':'A step-by-step guide to building a production-ready ML pipeline — from data preprocessing to model deployment.','content':'Building machine learning pipelines is one of the most important skills for any data scientist.\n\nIn this post I walk through how to build a production-ready pipeline using Python and scikit-learn, covering data preprocessing, feature engineering, model selection, and deployment patterns that scale.\n\nThe key insight is to encapsulate all preprocessing steps inside the pipeline so training and inference are always in sync. This eliminates training-serving skew, one of the most common ML bugs in production.','tags':'Python, Machine Learning, scikit-learn, Data Science','published':True},
                {'title':'Django REST Framework Best Practices 2025','slug':'drf-best-practices-2025','excerpt':'Key patterns for building scalable, secure REST APIs with Django REST Framework.','content':'After building dozens of APIs with Django REST Framework, here are the practices that consistently lead to clean, maintainable, and performant APIs.\n\nAlways version your APIs from day one. Use JWT for authentication. Paginate every list endpoint. Use ViewSets with routers to reduce boilerplate. Write serializer-level validation rather than view-level validation. These patterns compound — each one makes the next easier.\n\nThe biggest mistake I see junior developers make is building APIs without thinking about consumers. Design your API from the client perspective first, then implement it. You will ship better APIs faster.','tags':'Django, Python, REST API, Backend','published':True},
                {'title':'From Data to Decisions: Building a BI Dashboard','slug':'bi-dashboard-data-to-decisions','excerpt':'How I built a real-time BI dashboard processing 2M transactions daily for a Nairobi fintech.','content':'Data without context is just noise. In this post, I share how I built a BI dashboard that transforms raw transaction data into actionable insights for a Nairobi-based fintech company.\n\nThe architecture uses a Lambda approach: daily Spark batch jobs for historical aggregations, Kafka streams for real-time metrics, and PostgreSQL with Redis for the serving layer.\n\nAfter deploying the dashboard, the operations team reduced their reporting time from 3 hours per day to 15 minutes. More importantly, the fraud team identified a pattern that saved the company $50,000 in the first month alone.\n\nThe lesson: the value of data engineering is not in the technology — it is in the decisions it enables.','tags':'Data Science, Analytics, Python, Business Intelligence','published':True},
            ]
            for p in posts:
                BlogPost.objects.create(**p)
            self.stdout.write(self.style.SUCCESS(f'{len(posts)} posts created'))

        self.stdout.write(self.style.SUCCESS('\nSeed complete! Visit http://127.0.0.1:8000'))
