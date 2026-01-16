import os
import subprocess
import tempfile
import whisper
from docx import Document
from django.conf import settings
from datetime import datetime

# Variáveis globais
MODEL_DEVICE = os.getenv('MODEL_DEVICE', 'cpu')
MODEL = whisper.load_model("medium", device=MODEL_DEVICE)  # Load once


def _converter_para_wav(caminho_entrada: str) -> str:
    """
    Converte qualquer ficheiro de áudio/vídeo para WAV 16 kHz mono (sem compressão),
    garantindo máxima compatibilidade e precisão para o Whisper.
    """
    caminho_temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    caminho_temp.close()

    comando = [
        "ffmpeg", "-y", "-i", caminho_entrada,
        "-ar", "16000", "-ac", "1", "-vn",
        caminho_temp.name
    ]
    subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return caminho_temp.name


def transcrever_audio(caminho_audio: str) -> str:
    """
    Transcreve um ficheiro de áudio ou vídeo em português e
    guarda o resultado em 'MEDIA_ROOT/transcricao.docx'.
    """
    try:
        # 🔹 Converter o áudio/vídeo para WAV 16 kHz mono
        caminho_wav = _converter_para_wav(caminho_audio)

        # 🔹 Transcrever com o modelo (máxima precisão)
        resultado = MODEL.transcribe(caminho_wav, language="portuguese")
        transcricao = resultado["text"].strip()

        # 🔹 Garantir que MEDIA_ROOT existe
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        # 🔹 Gerar nome único para o arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_transcricao = os.path.join(settings.MEDIA_ROOT, f"transcricao_{timestamp}.docx")

        # 🔹 Criar novo documento DOCX
        doc = Document()
        doc.add_heading("Transcrição de Áudio/Vídeo", level=1)
        doc.add_heading(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", level=2)
        doc.add_paragraph(transcricao)
        
        # 🔹 Salvar documento
        try:
            doc.save(arquivo_transcricao)
            print(f"✅ Arquivo salvo em: {arquivo_transcricao}")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            raise

        return "✅ Transcrição concluída com sucesso!"
    except Exception as e:
        return f"❌ Erro na transcrição: {e}"
    finally:
        # 🔹 Limpar o ficheiro temporário
        try:
            os.remove(caminho_wav)
        except OSError:
            pass
