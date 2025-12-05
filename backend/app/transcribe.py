from transformers import (
    Wav2Vec2ForCTC,
    Wav2Vec2Processor,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)
import torch
import soundfile as sf
import numpy as np
from pathlib import Path
import torchaudio
import warnings

# Model cache to support multiple models
_MODEL_CACHE = {}

MODEL_MAP = {
    # Smaller, faster models better suited for real-time
    "wav2vec2-small": "facebook/wav2vec2-base-100h",
    "wav2vec2-base": "facebook/wav2vec2-base-960h",
    "whisper-small": "openai/whisper-small",
    # Larger, more accurate models for file upload
    "wav2vec2-large": "facebook/wav2vec2-large-960h",
    "whisper-base": "openai/whisper-base",
    "xlsr-53-large": "facebook/wav2vec2-large-xlsr-53",
}


def _is_whisper_model(model_path: str) -> bool:
    return "whisper" in model_path.lower()


def load_model(model_name: str = "wav2vec2-base"):
    """Load a model by name with memory optimization. Supports wav2vec2 and whisper.

    Returns (processor, model, model_type) where model_type is 'wav2vec2' or 'whisper'.
    """
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]

    model_path = MODEL_MAP.get(model_name)
    if model_path is None:
        raise ValueError(f"Unknown model name: {model_name}")

    try:
        if _is_whisper_model(model_path):
            processor = WhisperProcessor.from_pretrained(model_path)
            model = WhisperForConditionalGeneration.from_pretrained(
                model_path,
                low_cpu_mem_usage=True,
            )
            model_type = "whisper"
        else:
            processor = Wav2Vec2Processor.from_pretrained(model_path)
            model = Wav2Vec2ForCTC.from_pretrained(
                model_path,
                low_cpu_mem_usage=True,
            )
            model_type = "wav2vec2"

        model.eval()
        _MODEL_CACHE[model_name] = (processor, model, model_type)
        print(f"Loaded model: {model_name} -> {model_path} (type={model_type})")
        return processor, model, model_type

    except Exception as e:
        warnings.warn(f"Failed loading model {model_name} ({model_path}): {e}")
        # Fallback to base wav2vec2 if not already
        if model_name != "wav2vec2-base":
            return load_model("wav2vec2-base")
        # If base fails, raise an informative error
        raise RuntimeError(f"Could not load base model: {e}")


def _resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = 16000) -> np.ndarray:
    if orig_sr == target_sr:
        return audio
    # torchaudio expects shape [channels, time]
    if audio.ndim == 1:
        tensor = torch.from_numpy(audio).float().unsqueeze(0)
    else:
        tensor = torch.from_numpy(audio.T).float()
    resampler = torchaudio.transforms.Resample(orig_freq=orig_sr, new_freq=target_sr)
    resampled = resampler(tensor)
    resampled = resampled.squeeze(0).numpy() if resampled.ndim == 2 and resampled.shape[0] == 1 else resampled.numpy()
    return resampled


def transcribe_audio_path(path: str, model_name: str = "wav2vec2-base", chunk_size: int = 30):
    """Transcribe an audio file on disk using the requested model.

    - Resamples to 16 kHz when needed.
    - Processes in chunks (seconds) to limit memory use.
    - Supports both wav2vec2 (CTC) and Whisper models.
    """
    processor, model, model_type = load_model(model_name)

    audio, sr = sf.read(path)
    if audio is None or len(audio) == 0:
        raise ValueError("Empty or invalid audio file")

    # Convert to mono
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    # Resample to 16kHz (required by many models)
    target_sr = 16000
    if sr != target_sr:
        try:
            audio = _resample_audio(audio, sr, target_sr)
            sr = target_sr
        except Exception as e:
            warnings.warn(f"Resampling failed ({e}), continuing with original sample rate {sr}")

    max_length = int(chunk_size * sr)
    texts = []

    def _decode_chunk(chunk_np: np.ndarray):
        if model_type == "wav2vec2":
            inputs = processor(chunk_np, sampling_rate=sr, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = model(inputs.input_values).logits
            ids = torch.argmax(logits, dim=-1)
            return processor.batch_decode(ids)[0]
        else:
            # Whisper expects input_features rather than input_values; processor handles feature extraction
            inputs = processor(chunk_np, sampling_rate=sr, return_tensors="pt")
            # Some whisper models expect specific processor calls; use generate
            with torch.no_grad():
                generated_ids = model.generate(inputs.input_features)
            return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    if len(audio) > max_length:
        for i in range(0, len(audio), max_length):
            chunk = audio[i : i + max_length]
            texts.append(_decode_chunk(chunk))
        return " ".join(t for t in texts if t)

    return _decode_chunk(audio)


def transcribe_audio_np(audio_np: np.ndarray, sr: int = 16000, model_name: str = "wav2vec2-base"):
    processor, model, model_type = load_model(model_name)
    if audio_np.ndim > 1:
        audio_np = audio_np.mean(axis=1)

    # Resample if necessary
    if sr != 16000:
        audio_np = _resample_audio(audio_np, sr, 16000)
        sr = 16000

    if model_type == "wav2vec2":
        inputs = processor(audio_np, sampling_rate=sr, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = model(inputs.input_values).logits
        ids = torch.argmax(logits, dim=-1)
        return processor.batch_decode(ids)[0]
    else:
        inputs = processor(audio_np, sampling_rate=sr, return_tensors="pt")
        with torch.no_grad():
            generated_ids = model.generate(inputs.input_features)
        return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
