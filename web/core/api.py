from django.urls import path, include
from uploads_datasets import views as uploads_views

api_patterns = ([
    path('uploads/presign', uploads_views.presign),
    path('uploads/complete', uploads_views.complete),
], 'api')

urlpatterns = [
    path('api/', include(api_patterns)),
]
