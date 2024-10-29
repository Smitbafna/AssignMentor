

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages

def index(request):
    return HttpResponse("Hello, world. You're at the users index.")



@login_required
def Orgselect(request):
    return render(request, "users/Orgselect.html")  # Ensure this file exists


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect("Orgselect")  # Replace with the name of your dashboard URL pattern
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, "users/login.html")
