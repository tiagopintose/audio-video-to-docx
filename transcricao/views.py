from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .utils import transcrever_audio
from django.http import JsonResponse
import os
import tempfile
import datetime
import threading
import time
import json
import uuid
import moviepy.editor as mp

def index(request):
    """
    Renderiza a página principal. Não grava uploads aqui (o upload é feito por start_transcribe).
    Lista ficheiros existentes em MEDIA_ROOT para download.
    """
    context = {}

    # lista ficheiros em MEDIA_ROOT
    ficheiros = []
    try:
        media_root = settings.MEDIA_ROOT
        if os.path.isdir(media_root):
            entries = []
            for nome in os.listdir(media_root):
                caminho = os.path.join(media_root, nome)
                if os.path.isfile(caminho):
                    mtime = os.path.getmtime(caminho)
                    size_kb = os.path.getsize(caminho) / 1024
                    entries.append({
                        "nome": nome,
                        "tamanho": f"{size_kb:.1f} KB",
                        "mtime": mtime,
                    })
            # ordenar por último tempo de modificação (mais recente primeiro)
            entries.sort(key=lambda e: e["mtime"], reverse=True)
            # não precisamos expor mtime ao template, mas pode ficar se quiser
            ficheiros = entries
    except Exception:
        ficheiros = []

    context["ficheiros"] = ficheiros
    context["MEDIA_URL"] = settings.MEDIA_URL

    return render(request, "index.html", context)

def _write_progress(job_path, data):
    try:
        with open(job_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def start_transcribe(request):
    """
    Recebe upload via XHR, grava temporariamente e lança um thread que corre a transcrição.
    Retorna JSON com job_id.
    """
    if request.method != "POST" or "file" not in request.FILES:
        return JsonResponse({"error": "Método inválido ou ficheiro em falta"}, status=400)

    uploaded = request.FILES["file"]
    ext = os.path.splitext(uploaded.name)[1].lower()

    job_id = uuid.uuid4().hex
    jobs_dir = os.path.join(tempfile.gettempdir(), "transcribe_jobs")
    os.makedirs(jobs_dir, exist_ok=True)
    job_file = os.path.join(jobs_dir, f"{job_id}.json")

    # grava upload para ficheiro temporário
    tmp_input = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    try:
        for chunk in uploaded.chunks():
            tmp_input.write(chunk)
        tmp_input.flush()
        tmp_input_path = tmp_input.name
    finally:
        tmp_input.close()

    # estado inicial
    _write_progress(job_file, {"status": "queued", "percent": 0, "message": "A preparar...", "filename": None})

    def background_job(input_path, extension, job_path):
        done_event = threading.Event()

        # updater incrementa percent gradualmente até a conclusão (simulação)
        def updater():
            pct = 3
            _write_progress(job_path, {"status": "processing", "percent": pct, "message": "A processar...", "filename": None})
            while not done_event.is_set():
                pct = min(95, pct + 4)
                _write_progress(job_path, {"status": "processing", "percent": pct, "message": "A processar...", "filename": None})
                time.sleep(2)
        up_thread = threading.Thread(target=updater, daemon=True)
        up_thread.start()

        try:
            audio_path = None
            # se vídeo, extrai áudio
            if extension in [".mp4", ".mkv", ".avi", ".mov"]:
                tf_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                audio_path = tf_audio.name
                tf_audio.close()
                video = mp.VideoFileClip(input_path)
                try:
                    video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                finally:
                    video.close()
                _write_progress(job_path, {"status": "processing", "percent": 10, "message": "Áudio extraído", "filename": None})
                work_path = audio_path
            else:
                work_path = input_path

            # chama a função de transcrição (bloqueante)
            trans_msg = transcrever_audio(work_path)  # função existente
            # após transcrição, verifica se transcricao.docx foi criado em MEDIA_ROOT e renomeia para único
            original_name = "transcricao.docx"
            original_path = os.path.join(settings.MEDIA_ROOT, original_name)
            result_name = None
            if os.path.exists(original_path):
                ts = datetime.datetime.now().strftime("%Y%m%dT%H%M")
                result_name = f"transcricao_{ts}.docx"
                result_path = os.path.join(settings.MEDIA_ROOT, result_name)
                os.replace(original_path, result_path)
                _write_progress(job_path, {"status": "done", "percent": 100, "message": trans_msg or "Concluído", "filename": result_name})
            else:
                # nenhum ficheiro escrito; grava mensagem de erro parcial
                _write_progress(job_path, {"status": "done", "percent": 100, "message": trans_msg or "Concluído (sem ficheiro gerado)", "filename": None})
        except Exception as e:
            _write_progress(job_path, {"status": "error", "percent": 100, "message": str(e), "filename": None})
        finally:
            done_event.set()
            up_thread.join(timeout=1)
            # limpar temporários
            try:
                if audio_path and os.path.exists(audio_path):
                    os.remove(audio_path)
            except Exception:
                pass
            try:
                if input_path and os.path.exists(input_path):
                    os.remove(input_path)
            except Exception:
                pass

    t = threading.Thread(target=background_job, args=(tmp_input_path, ext, job_file), daemon=True)
    t.start()

    return JsonResponse({"job_id": job_id})

def job_status(request, job_id):
    jobs_dir = os.path.join(tempfile.gettempdir(), "transcribe_jobs")
    job_file = os.path.join(jobs_dir, f"{job_id}.json")
    if not os.path.exists(job_file):
        return JsonResponse({"error": "Job não encontrado"}, status=404)
    try:
        with open(job_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JsonResponse({"error": "Erro a ler estado", "detail": str(e)}, status=500)
    return JsonResponse(data)
