from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, SignupForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    form = LoginForm(request.POST or None)
    message = None
    if request.method == "POST" and form.is_valid():
        user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
        if user:
            login(request, user)
            if form.cleaned_data.get("remember_me"):
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(0)
            return redirect("dashboard:dashboard")
        else:
            message = "Invalid username or password."
    return render(request, "accounts/login.html", {"form": form, "message": message})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:login")
    return render(request, "accounts/signup.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("accounts:login")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


# Create your views here.
