import os
import whisper
from django.conf import settings

# Carrega o modelo apenas uma vez no início da aplicação
MODEL_DEVICE = os.getenv('MODEL_DEVICE', 'cpu')
MODEL = whisper.load_model("medium", device=MODEL_DEVICE)
