
# web/core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def home_redirect(request):
    return redirect('core:principal' if request.user.is_authenticated else 'core:login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') or ''
        password = request.POST.get('password') or ''
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:principal')
        return render(request, 'core/login.html', {'erro_login': True})
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('core:login')

@login_required
def principal(request):
    user = request.user
    display_name = user.get_full_name() or user.username
    credits = getattr(getattr(user, "profile", None), "credits", None)
    plan = getattr(getattr(user, "profile", None), "plan_name", None)
    return render(request, "core/principal.html", {
        "display_name": display_name,
        "credits": credits,
        "plan": plan,
    })

# Placeholders das outras seções já usadas na principal

@login_required
def usuario(request):
    return render(request, "core/placeholder.html", {"title": "Usuário"})

@login_required
def creditos(request):
    return render(request, "core/placeholder.html", {"title": "Créditos"})

@login_required
def guias(request):
    return render(request, "core/placeholder.html", {"title": "Guias & Boas Práticas"})

# Opcional: compat de demo
def principal_demo(request):
    ctx = {"display_name": "Admin Demo", "plan": "Básico", "credits": 42}
    return render(request, "core/principal.html", ctx)


