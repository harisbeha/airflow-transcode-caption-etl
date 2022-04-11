from django.urls import path
from frontend import views

urlpatterns = [
    path('transcription/', views.OrderTranscriptionView.as_view(), name='transcription'),
    path('translation/', views.OrderTranslationView.as_view(), name='translation'),
    path('audio_description/', views.OrderAudioDescriptionView.as_view(), name='audio_description'),
]
