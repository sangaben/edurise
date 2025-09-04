from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile

class Command(BaseCommand):
    help = 'Create sample teacher accounts for testing'

    def handle(self, *args, **options):
        teachers = [
            {
                'username': 'john.math',
                'email': 'john.math@edurise.com',
                'first_name': 'John',
                'last_name': 'Mathematics',
                'password': 'teacher123',
                'subject': 'mathematics'
            },
            {
                'username': 'sarah.science',
                'email': 'sarah.science@edurise.com',
                'first_name': 'Sarah',
                'last_name': 'Science',
                'password': 'teacher123',
                'subject': 'sciences'
            },
            {
                'username': 'david.english',
                'email': 'david.english@edurise.com',
                'first_name': 'David',
                'last_name': 'Languages',
                'password': 'teacher123',
                'subject': 'languages'
            }
        ]

        for teacher_data in teachers:
            # Check if user already exists
            if not User.objects.filter(username=teacher_data['username']).exists():
                user = User.objects.create_user(
                    username=teacher_data['username'],
                    email=teacher_data['email'],
                    first_name=teacher_data['first_name'],
                    last_name=teacher_data['last_name'],
                    password=teacher_data['password']
                )
                
                # Update profile to be a teacher
                profile = user.profile
                profile.role = 'teacher'
                profile.subject_specialization = teacher_data['subject']
                profile.is_verified = True
                profile.bio = f"Experienced {teacher_data['subject']} teacher with passion for education."
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created teacher: {user.get_full_name()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Teacher already exists: {teacher_data["username"]}')
                )