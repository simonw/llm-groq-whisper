import click
import httpx
import io
import json
import llm
from typing import Optional, Literal

GROQ_MODELS = [
    "whisper-large-v3-turbo",
    "distil-whisper-large-v3-en",
    "whisper-large-v3",
]

ResponseFormat = Literal["json", "verbose_json", "text"]


@llm.hookimpl
def register_commands(cli):
    @cli.command()
    @click.argument("audio_file", type=click.File("rb"))
    @click.option("--key", "api_key", help="Groq API key to use")
    @click.option(
        "--model",
        type=click.Choice(GROQ_MODELS),
        default="whisper-large-v3-turbo",
        help="Whisper model to use",
    )
    @click.option(
        "--response-format",
        type=click.Choice(["json", "verbose_json", "text"]),
        default="text",
        help="Response format",
    )
    @click.option(
        "--language",
        help="Language code (e.g., 'en' for English). Only for whisper-large-v3-turbo and whisper-large-v3",
    )
    @click.option("--temperature", type=float, help="Temperature between 0 and 1")
    @click.option(
        "--prompt", help="Optional context or spelling guidance (max 224 tokens)"
    )
    @click.option(
        "--translate",
        is_flag=True,
        help="Use translation endpoint instead of transcription",
    )
    def groq_whisper(
        audio_file,
        api_key: str,
        model: str,
        response_format: ResponseFormat,
        language: Optional[str],
        temperature: Optional[float],
        prompt: Optional[str],
        translate: bool,
    ):
        """
        Run transcriptions or translations using the Groq Whisper API

        Usage:
        \b
            llm groq-whisper audio.mp3 > output.txt
            cat audio.mp3 | llm groq-whisper - > output.txt

        Examples:
        \b
            # Basic transcription
            llm groq-whisper audio.mp3

            # Translation to English
            llm groq-whisper --translate audio.mp3

            # Transcription with specific model and language
            llm groq-whisper --model whisper-large-v3 --language fr audio.mp3

            # Detailed JSON output with timestamps
            llm groq-whisper --response-format verbose_json audio.mp3
        """
        # Read the entire content into memory first
        audio_content = audio_file.read()
        audio_file.close()

        key = llm.get_key(api_key, "groq")
        if not key:
            raise click.ClickException("Groq API key is required")

        # Validate temperature if provided
        if temperature is not None and not (0 <= temperature <= 1):
            raise click.ClickException("Temperature must be between 0 and 1")

        # Validate language option
        if language and model not in ["whisper-large-v3-turbo", "whisper-large-v3"]:
            raise click.ClickException(
                "Language option is only supported for whisper-large-v3-turbo and whisper-large-v3 models"
            )

        try:
            result = process_audio(
                audio_content=audio_content,
                api_key=key,
                model=model,
                response_format=response_format,
                language=language,
                temperature=temperature,
                prompt=prompt,
                translate=translate,
            )
            if isinstance(result, dict):
                click.echo(json.dumps(result, indent=2))
            else:
                click.echo(result)
        except httpx.HTTPError as ex:
            raise click.ClickException(str(ex))


def process_audio(
    audio_content: bytes,
    api_key: str,
    model: str,
    response_format: ResponseFormat = "text",
    language: Optional[str] = None,
    temperature: Optional[float] = None,
    prompt: Optional[str] = None,
    translate: bool = False,
) -> str:
    """
    Process audio content using Groq's Whisper API.

    Args:
        audio_content (bytes): The audio content as bytes
        api_key (str): Groq API key
        model (str): Whisper model to use
        response_format (str): Output format (json, verbose_json, or text)
        language (str, optional): Language code for transcription
        temperature (float, optional): Temperature between 0 and 1
        prompt (str, optional): Context or spelling guidance
        translate (bool): Whether to use translation endpoint

    Returns:
        str: The transcribed or translated text

    Raises:
        httpx.RequestError: If the API request fails
    """
    endpoint = "translations" if translate else "transcriptions"
    url = f"https://api.groq.com/openai/v1/audio/{endpoint}"

    headers = {"Authorization": f"Bearer {api_key}"}

    # Prepare audio file
    audio_file = io.BytesIO(audio_content)
    # Use a generic name that matches one of the supported formats
    audio_file.name = "audio.mp3"

    files = {"file": audio_file}
    data = {"model": model, "response_format": response_format}

    # Add optional parameters if provided
    if language:
        data["language"] = language
    if temperature is not None:
        data["temperature"] = temperature
    if prompt:
        data["prompt"] = prompt

    with httpx.Client() as client:
        response = client.post(
            url, headers=headers, files=files, data=data, timeout=None
        )
        response.raise_for_status()

        if response_format == "text":
            return response.text.strip()
        return response.json()
