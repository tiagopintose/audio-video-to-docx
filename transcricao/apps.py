from django.apps import AppConfig
import whisper

class TranscritorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcricao'  

    def ready(self):
        """
        Carrega o modelo Whisper uma única vez no arranque da app.
        """
        from . import utils

        print("🔊 A carregar o modelo Whisper (large)... isto pode demorar um pouco.")
        utils.MODEL = whisper.load_model("large", device="cpu")
        print("✅ Modelo Whisper carregado e pronto!")
