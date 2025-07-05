import torch
import whisper
import warnings

from config import WHISPER_MODEL_SIZE

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


def load_whisper_model():
    """Загружает Whisper-модель в зависимости от доступности CUDA."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Whisper model loading on: {device}")
    model = whisper.load_model(WHISPER_MODEL_SIZE, device=device)
    print("Whisper model loaded.")
    
    return model, device


async def transcribe_audio(model, file_path: str, language: str = None) -> str:
    """Транскрибирует аудиофайл в текст. Автоматически определяет язык, если указано 'auto'."""
    try:
        transcription_params = {
            "audio": file_path,
            "fp16": False if model.device == "cpu" else True
        }

        if language not in (None, "auto"):
            transcription_params["language"] = language

        result = model.transcribe(**transcription_params)

        return result["text"].strip()

    except Exception as e:
        return f"[Ошибка при распознавании речи: {str(e)}]"