from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import User
from django.contrib import messages
from .models import*
from django.db.models import F


def home(request):
    return render(request,'home.html')
# Register a User (Candidate or Admin)
def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_role = request.POST.get('role')  # Get role (admin or candidate)

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("register_user")

        # Password validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('register_user')
        
         # Validate role
        if user_role not in ['admin', 'candidate']:
            messages.error(request, "Invalid role specified.")
            return redirect('register_user')

        # Create User based on role selection
        if user_role == 'admin':
            user = User.objects.create_user(username=username, email=email, password=password, is_admin=True)
        else:
            user = User.objects.create_user(username=username, email=email, password=password, is_candidate=True)

        user.is_active = False  # Inactive until email is verified
        user.save()
        
        profile = Profile(user=user)  # Create a Profile linked to the user
        profile.save()  # Save the profile

        # Send verification email
        token = get_random_string(32)
        user.profile.token = token
        user.profile.save()
        
            # Send verification email with custom content
        send_mail(
            'Email Verification !!',
            f"""
            Hi {user.username},

            Welcome to Projectfolio! We are excited to have you join our platform. 
            Please verify your email address by clicking the link below:

            http://127.0.0.1:8000/verify/{token}/

            This will activate your account, and you'll be able to start exploring our platform.

            If you did not sign up for this account, please disregard this email.

            """,
            'annanyatiwary4@gmail.com',  # Use a dedicated support email instead of 'admin'
            [email],
        )

        
        messages.success(request, "Account created. Please verify your email.")
        return redirect('login')

    return render(request, 'register.html')


# Email Verification
def verify_email(request, token):
    try:
        user = User.objects.get(profile__token=token)
        user.is_active = True
        user.is_verified = True
        user.profile.token = None
        user.save()
        messages.success(request, "Email verified successfully!")
        return redirect('login')
    except User.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('login')

# Login

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Custom authenticate method for email
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user and user.check_password(password):
            if not user.is_verified:
                messages.error(request, "Please verify your email first.")
                return redirect('login')

            login(request, user)
            if user.is_admin:
                return redirect('admin_dashboard')  # Admin dashboard
            elif user.is_candidate:
                return redirect('candidate_dashboard')  # Candidate dashboard
            else:
                return redirect('login')  # In case no role is assigned

        messages.error(request, "Invalid credentials.")
        return redirect('login')
    else:
        return render(request, 'login.html')



# Logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

def admin_dashboard(request):
    projects = Project.objects.all()

    # Calculate progress for each project
    for project in projects:
        total_tasks = project.total_tasks
        # Correctly access the assignments related to this project
        completed_tasks = sum([assignment.completed_tasks for assignment in project.assignments.all()])
        project.progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks else 0

    return render(request, 'admin_dashboard.html', {
        'projects': projects,
    })

