"""
Voice model configurations for Piper TTS.
Generated from the official Piper voices repository.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class VoiceModel:
    """Voice model configuration."""
    id: str
    language: str
    language_code: str
    language_name: str
    speaker: str
    quality: str
    model_url: str
    config_url: str
    gender: Optional[str] = None
    description: Optional[str] = None


# Voice models configuration
VOICE_MODELS: Dict[str, VoiceModel] = {
    # English (US) voices
    "en_US-lessac-medium": VoiceModel(
        id="en_US-lessac-medium",
        language="English (US)",
        language_code="en_US",
        language_name="English",
        speaker="lessac",
        quality="medium",
        gender="female",
        description="High quality female American English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    ),
    "en_US-lessac-high": VoiceModel(
        id="en_US-lessac-high",
        language="English (US)",
        language_code="en_US",
        language_name="English",
        speaker="lessac",
        quality="high",
        gender="female",
        description="Very high quality female American English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx.json"
    ),
    "en_US-ryan-medium": VoiceModel(
        id="en_US-ryan-medium",
        language="English (US)",
        language_code="en_US",
        language_name="English",
        speaker="ryan",
        quality="medium",
        gender="male",
        description="High quality male American English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/medium/en_US-ryan-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json"
    ),
    "en_US-ryan-high": VoiceModel(
        id="en_US-ryan-high",
        language="English (US)",
        language_code="en_US",
        language_name="English",
        speaker="ryan",
        quality="high",
        gender="male",
        description="Very high quality male American English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/ryan/high/en_US-ryan-high.onnx.json"
    ),
    "en_US-amy-medium": VoiceModel(
        id="en_US-amy-medium",
        language="English (US)",
        language_code="en_US",
        language_name="English",
        speaker="amy",
        quality="medium",
        gender="female",
        description="Natural female American English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
    ),
    "en_US-joe-medium": VoiceModel(
        id="en_US-joe-medium",
        language="English (US)",
        language_code="en_US",
        language_name="English",
        speaker="joe",
        quality="medium",
        gender="male",
        description="Clear male American English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/joe/medium/en_US-joe-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/joe/medium/en_US-joe-medium.onnx.json"
    ),

    # English (UK) voices
    "en_GB-alan-medium": VoiceModel(
        id="en_GB-alan-medium",
        language="English (UK)",
        language_code="en_GB",
        language_name="English",
        speaker="alan",
        quality="medium",
        gender="male",
        description="British male English voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
    ),
    "en_GB-cori-high": VoiceModel(
        id="en_GB-cori-high",
        language="English (UK)",
        language_code="en_GB",
        language_name="English",
        speaker="cori",
        quality="high",
        gender="female",
        description="High quality British female voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/cori/high/en_GB-cori-high.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_GB/cori/high/en_GB-cori-high.onnx.json"
    ),

    # German voices
    "de_DE-thorsten-medium": VoiceModel(
        id="de_DE-thorsten-medium",
        language="German",
        language_code="de_DE",
        language_name="Deutsch",
        speaker="thorsten",
        quality="medium",
        gender="male",
        description="German male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"
    ),
    "de_DE-thorsten-high": VoiceModel(
        id="de_DE-thorsten-high",
        language="German",
        language_code="de_DE",
        language_name="Deutsch",
        speaker="thorsten",
        quality="high",
        gender="male",
        description="High quality German male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json"
    ),

    # French voices
    "fr_FR-siwis-medium": VoiceModel(
        id="fr_FR-siwis-medium",
        language="French",
        language_code="fr_FR",
        language_name="Français",
        speaker="siwis",
        quality="medium",
        gender="female",
        description="French female voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
    ),
    "fr_FR-tom-medium": VoiceModel(
        id="fr_FR-tom-medium",
        language="French",
        language_code="fr_FR",
        language_name="Français",
        speaker="tom",
        quality="medium",
        gender="male",
        description="French male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/fr/fr_FR/tom/medium/fr_FR-tom-medium.onnx.json"
    ),

    # Spanish voices
    "es_ES-davefx-medium": VoiceModel(
        id="es_ES-davefx-medium",
        language="Spanish (Spain)",
        language_code="es_ES",
        language_name="Español",
        speaker="davefx",
        quality="medium",
        gender="male",
        description="Spanish male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
    ),
    "es_MX-claude-high": VoiceModel(
        id="es_MX-claude-high",
        language="Spanish (Mexico)",
        language_code="es_MX",
        language_name="Español",
        speaker="claude",
        quality="high",
        gender="male",
        description="Mexican Spanish male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high/es_MX-claude-high.onnx.json"
    ),

    # Italian voices
    "it_IT-paola-medium": VoiceModel(
        id="it_IT-paola-medium",
        language="Italian",
        language_code="it_IT",
        language_name="Italiano",
        speaker="paola",
        quality="medium",
        gender="female",
        description="Italian female voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/paola/medium/it_IT-paola-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json"
    ),

    # Portuguese voices
    "pt_BR-faber-medium": VoiceModel(
        id="pt_BR-faber-medium",
        language="Portuguese (Brazil)",
        language_code="pt_BR",
        language_name="Português",
        speaker="faber",
        quality="medium",
        gender="male",
        description="Brazilian Portuguese male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json"
    ),

    # Russian voices
    "ru_RU-denis-medium": VoiceModel(
        id="ru_RU-denis-medium",
        language="Russian",
        language_code="ru_RU",
        language_name="Русский",
        speaker="denis",
        quality="medium",
        gender="male",
        description="Russian male voice",
        model_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx",
        config_url="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/ru/ru_RU/denis/medium/ru_RU-denis-medium.onnx.json"
    ),
}


def get_available_voices() -> List[VoiceModel]:
    """Get list of all available voice models."""
    return list(VOICE_MODELS.values())


def get_voice_by_id(voice_id: str) -> Optional[VoiceModel]:
    """Get voice model by ID."""
    return VOICE_MODELS.get(voice_id)


def get_voices_by_language(language_code: str) -> List[VoiceModel]:
    """Get voices filtered by language code."""
    return [voice for voice in VOICE_MODELS.values() if voice.language_code == language_code]


def get_default_voice() -> VoiceModel:
    """Get the default voice model."""
    return VOICE_MODELS["en_US-lessac-medium"]