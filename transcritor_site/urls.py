from django.contrib import admin
from django.urls import path
from transcricao import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("start_transcribe/", views.start_transcribe, name="start_transcribe"),
    path("status/<str:job_id>/", views.job_status, name="job_status"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)