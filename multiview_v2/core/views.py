from django.shortcuts import render
from django.http import HttpResponse

def principal(request):
    return render(request, "core/principal.html")

def health(request):
    return HttpResponse("OK Multiview V2", content_type="text/plain")

def creditos(request):
    return render(request, "core/creditos.html")

def guias(request):
    return render(request, "core/guias.html")

def usuario(request):
    return render(request, "core/usuario.html")

def usuarios(request):
    return render(request, "core/usuarios.html")