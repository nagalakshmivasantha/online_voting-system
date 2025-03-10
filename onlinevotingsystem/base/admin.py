from django.contrib import admin
from .models import Profile,User,Election,Candidate

# Register your models here.
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Election)

admin.site.register(Candidate)

