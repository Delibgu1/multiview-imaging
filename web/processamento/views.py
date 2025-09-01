from django.http import HttpResponse

def index(request):
    return HttpResponse("Fila de Processamento • OK (placeholder)")
