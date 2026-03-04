"""Stage 5: Text-to-speech voiceover generation using Azure Cognitive Services."""

import os

import azure.cognitiveservices.speech as speechsdk

from pipeline.config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, TTS_VOICE

__all__ = ["generate_voiceover", "generate_all_voiceovers"]


def generate_voiceover(
    text: str,
    output_path: str,
    voice: str | None = None,
    rate: str = "0%",
    pitch: str = "0%",
) -> str:
    """Generate a voiceover audio file from text.

    Parameters
    ----------
    text : str
        Narration text.
    output_path : str
        Path for the output .mp3 file.
    voice : str
        Azure TTS voice name.
    rate : str
        Speech rate adjustment (e.g. "-10%", "+20%").
    pitch : str
        Pitch adjustment.

    Returns
    -------
    str
        Path to the generated audio file.
    """
    if voice is None:
        voice = TTS_VOICE

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    # SSML for fine control
    ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
          xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='en-US'>
    <voice name='{voice}'>
        <prosody rate='{rate}' pitch='{pitch}'>
            {_escape_ssml(text)}
        </prosody>
    </voice>
</speak>"""

    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return output_path
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        raise RuntimeError(
            f"TTS failed: {cancellation.reason} - {cancellation.error_details}"
        )
    else:
        raise RuntimeError(f"TTS failed with reason: {result.reason}")


def generate_all_voiceovers(
    narrations: dict[int, str],
    output_dir: str,
    voice: str | None = None,
) -> dict[int, str]:
    """Generate voiceovers for all scenes.

    Parameters
    ----------
    narrations : dict[int, str]
        Mapping of scene_id -> narration text.
    output_dir : str
        Directory for output audio files.

    Returns
    -------
    dict[int, str]
        Mapping of scene_id -> audio file path.
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    for scene_id, text in narrations.items():
        output_path = os.path.join(output_dir, f"scene_{scene_id}.mp3")
        print(f"Generating voiceover for scene {scene_id}...")
        try:
            path = generate_voiceover(text, output_path, voice=voice)
            results[scene_id] = path
            print(f"  Audio saved: {path}")
        except Exception as e:
            print(f"  TTS failed for scene {scene_id}: {e}")

    return results


def _escape_ssml(text: str) -> str:
    """Escape special characters for SSML."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
