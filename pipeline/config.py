"""Configuration for the paper-to-animation pipeline."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Scene Planning (Anthropic) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PLANNER_MODEL = "claude-sonnet-4-5-20250929"

# --- Code Generation (Azure DeepSeek) ---
AZURE_DEEPSEEK_ENDPOINT = os.getenv("AZURE_DEEPSEEK_ENDPOINT")
AZURE_DEEPSEEK_KEY = os.getenv("AZURE_DEEPSEEK_KEY")
CODEGEN_MODEL = "DeepSeek-V3.2"

# --- Vision QA (Azure OpenAI) ---
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
VISION_MODEL = "gpt-4o"

# --- TTS (Azure Cognitive Services) ---
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")
TTS_VOICE = "en-US-AriaNeural"

# --- Rendering ---
MANIM_QUALITY = "-qh"  # High quality (1080p)
MAX_RETRIES = 5
RENDER_TIMEOUT = 120  # seconds per scene

# --- Output ---
OUTPUT_DIR = os.getenv("BANIM_OUTPUT_DIR", "output")
TEMP_DIR = os.getenv("BANIM_TEMP_DIR", "/tmp/banim")

# --- Plugin routing keywords ---
PLUGIN_ROUTING = {
    "manim": r"equation|integral|derivative|matrix|graph|function|proof|theorem|number|plot|axes|coordinate",
    "chanim": r"molecule|reaction|compound|bond|orbital|element|periodic|chemical",
    "banim": r"DNA|RNA|protein|cell|amino|peptide|ribosome|membrane|gene|codon|enzyme|CRISPR|nucleotide|helix|transcription|translation|replication",
}
