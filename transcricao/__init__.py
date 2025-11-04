import os
import whisper
from django.conf import settings

print("🔊 A carregar o modelo Whisper (large)... isto pode demorar um pouco.")
MODEL_DEVICE = os.getenv('MODEL_DEVICE', 'cpu')
MODEL = whisper.load_model("large", device=MODEL_DEVICE)
print("✅ Modelo Whisper carregado com sucesso!")
