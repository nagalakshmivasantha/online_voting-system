from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Election, Candidate, Profile

def home(request):
    return render(request, 'home.html')

# Register a User (Candidate or Admin)
def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        user_role = request.POST.get('role')  # Get role (admin or candidate)

        # Check if passwords match
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

        user.save()

        # Create a Profile linked to the user
        profile = Profile(user=user)
        profile.save()

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


# Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_admin:
                return redirect('admin_dashboard')  # Admin dashboard
            elif user.is_candidate:
                return redirect('candidate_dashboard')  # Candidate dashboard
            else:
                return redirect('login')  # In case no role is assigned

        messages.error(request, "Invalid credentials.")
        return redirect('login')

    return render(request, 'login.html')


# Logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


# Admin Dashboard
def admin_dashboard(request):
    elections = Election.objects.all()
    return render(request, 'admin_dashboard.html', {'elections': elections})


def create_election(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        

        # Check if all fields are filled
        if not title or not start_date or not end_date:
            messages.error(request, "Please fill all required fields.")
            return redirect('admin_dashboard')

        # Create the Election
        election = Election.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_by=request.user
        )
        election.save()
        messages.success(request, "Election created successfully!")
        return redirect('admin_dashboard')

    return redirect('admin_dashboard')


@login_required
def add_candidate(request, election_id):
    if not request.user.is_admin:
        messages.error(request, "You do not have permission to add candidates.")
        return redirect('dashboard')

    election = get_object_or_404(Election, id=election_id)

    if request.method == "POST":
        user_id = request.POST.get('user_id')  # Assuming candidates are registered users
        party = request.POST.get('party')
        bio = request.POST.get('bio')

        user = get_object_or_404(User, id=user_id)

        Candidate.objects.create(
            user=user, election=election, party=party, bio=bio
        )
        messages.success(request, "Candidate added successfully!")
        return redirect('dashboard')

    users = User.objects.filter(is_candidate=True)  # Fetching only candidate users
    return render(request, 'admin/add_candidate.html', {'election': election, 'users': users})
