import os
import whisper
from django.conf import settings
import gc

# Inicializar como None - será carregado apenas quando necessário
MODEL = None
MODEL_DEVICE = os.getenv('MODEL_DEVICE', 'cpu')
