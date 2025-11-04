from django.apps import AppConfig
from django.conf import settings
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

class TranscritorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcricao'  

    def ready(self):
        """
        Inicializa a app
        """
        from . import utils  # importa utils para registrar as variáveis globais
