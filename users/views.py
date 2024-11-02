

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from ars.models import Organization
import os
from django.conf import settings
from django.http import FileResponse, Http404

def index(request):
    return render(request, 'users/index.html')


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect("Orgselect")  
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "users/login.html")

def loginoauth(request):
    # Path to the React app's index.html
    react_app_path = os.path.join(settings.BASE_DIR, 'frontend', 'oauth', 'dist', 'index.html')
    
    try:
        return FileResponse(open(react_app_path, 'rb'))
    except FileNotFoundError:
        raise Http404("React app not found.")




@login_required
def Orgselect(request):
    organization = Organization.objects.all()
    context = {
        'organization': organization
    }
    return render(request,'users/Orgselect.html',context)
