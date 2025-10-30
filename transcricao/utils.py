import os
import subprocess
import tempfile
from docx import Document
from django.conf import settings

# 🔹 Será definido pelo __init__.py no arranque
MODEL = None


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
    global MODEL
    if MODEL is None:
        raise RuntimeError("O modelo Whisper ainda não foi carregado. Verifica o __init__.py da app.")

    # 🔹 Converter o áudio/vídeo para WAV 16 kHz mono
    caminho_wav = _converter_para_wav(caminho_audio)

    try:
        # 🔹 Transcrever com o modelo pré-carregado (máxima precisão)
        resultado = MODEL.transcribe(caminho_wav, language="portuguese")
        transcricao = resultado["text"].strip()

        # 🔹 Caminho final do ficheiro DOCX
        arquivo_transcricao = os.path.join(settings.MEDIA_ROOT, "transcricao.docx")

        # 🔹 Criar ou abrir o DOCX existente
        if not os.path.exists(arquivo_transcricao):
            doc = Document()
            doc.add_heading("Transcrições", level=1)
            doc.save(arquivo_transcricao)

        doc = Document(arquivo_transcricao)
        doc.add_heading("Nova Transcrição", level=2)
        doc.add_paragraph(transcricao)
        doc.save(arquivo_transcricao)

        return "✅ Transcrição concluída com sucesso!"
    except Exception as e:
        return f"❌ Erro na transcrição: {e}"
    finally:
        # 🔹 Limpar o ficheiro temporário
        try:
            os.remove(caminho_wav)
        except OSError:
            pass
