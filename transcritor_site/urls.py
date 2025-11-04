from django.contrib import admin
from django.urls import path
from transcricao import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path("", views.index, name="index"),
    path("start_transcribe/", views.start_transcribe, name="start_transcribe"),
    path("status/<str:job_id>/", views.job_status, name="job_status"),
    path("delete/<str:filename>/", views.delete_file, name="delete_file"),
    # Servir arquivos media mesmo com DEBUG=False
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Em desenvolvimento, servir arquivos estáticos
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)