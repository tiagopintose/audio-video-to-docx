from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("start_transcribe/", views.start_transcribe, name="start_transcribe"),
    path("status/<str:job_id>/", views.job_status, name="job_status"),
]