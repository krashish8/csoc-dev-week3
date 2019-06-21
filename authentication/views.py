from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,authenticate
# Create your views here.
from django.contrib import messages, auth
from django.contrib.auth.models import User

def loginView(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('index')
        else:
            messages.error(request, 'Invalid Credentials')
    return render(request, 'login.html')

def logoutView(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('index')

def registerView(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if not username.isalnum():
                messages.error(request, 'Username must contain only letters and numbers')
            elif len(password) < 6:
                messages.error(request, 'Password length must be atleast 6')
            elif User.objects.filter(username=username):
                messages.error(request, 'The username is already taken')
                return redirect('register')
            elif User.objects.filter(email=email):
                messages.error(request, 'The email is already taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.save()
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')
    return render(request, 'register.html')