from django.urls import path
from .views import *


urlpatterns=[
    path('',home,name='home'),
    path('register/', register_user, name='register_user'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('create-election/', create_election, name='create_election'),
    path('add-candidate/<int:election_id>/', add_candidate, name='add_candidate'),
 
]