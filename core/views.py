from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import LoginForm
from .models import WatchlistItem, Preference

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            # Handle remember me
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(60*60*24*30)  # 30 days
            else:
                request.session.set_expiry(0)  # expires on browser close
            return redirect('dashboard')
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login_custom')

@login_required
def dashboard(request):
    pref, _ = Preference.objects.get_or_create(user=request.user)
    watchlist = WatchlistItem.objects.filter(user=request.user)
    return render(request, 'core/dashboard.html', {'pref': pref, 'watchlist': watchlist})

@login_required
def add_watchlist(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker','').upper()[:16]
        if ticker:
            WatchlistItem.objects.get_or_create(user=request.user, ticker=ticker)
    return redirect('dashboard')

@login_required
def remove_watchlist(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker','').upper()[:16]
        if ticker:
            WatchlistItem.objects.filter(user=request.user, ticker=ticker).delete()
    return redirect('dashboard')
