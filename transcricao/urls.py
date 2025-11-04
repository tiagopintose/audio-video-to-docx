from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("start_transcribe/", views.start_transcribe, name="start_transcribe"),
    path("status/<str:job_id>/", views.job_status, name="job_status"),
    path("delete/<str:filename>/", views.delete_file, name="delete_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)