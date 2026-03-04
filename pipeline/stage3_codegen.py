"""Stage 3: Manim code generation using DeepSeek-V3.2 on Azure."""

import re
from pathlib import Path

from openai import AzureOpenAI

from pipeline.config import (
    AZURE_DEEPSEEK_ENDPOINT,
    AZURE_DEEPSEEK_KEY,
    CODEGEN_MODEL,
)
from pipeline.stage2_planner import SceneSpec

__all__ = ["generate_scene_code", "generate_all_scenes"]

CODEGEN_SYSTEM_PROMPT = ""
_prompt_path = Path(__file__).parent.parent / "prompts" / "codegen_system.txt"
if _prompt_path.exists():
    CODEGEN_SYSTEM_PROMPT = _prompt_path.read_text()


def _get_client() -> AzureOpenAI:
    return AzureOpenAI(
        azure_endpoint=AZURE_DEEPSEEK_ENDPOINT,
        api_key=AZURE_DEEPSEEK_KEY,
        api_version="2024-12-01-preview",
    )


def generate_scene_code(scene: SceneSpec, retry_error: str | None = None) -> str:
    """Generate executable Manim Python code for a single scene.

    Parameters
    ----------
    scene : SceneSpec
        Scene specification from the planner.
    retry_error : str or None
        If provided, this is the error from a previous render attempt.
        The model should fix the code based on this error.

    Returns
    -------
    str
        Executable Python code for the scene.
    """
    client = _get_client()

    system = CODEGEN_SYSTEM_PROMPT or _default_codegen_system()

    if retry_error:
        user_prompt = f"""The following Manim scene code failed to render. Fix the error.

Scene description: {scene.description}

Error:
{retry_error}

Generate the COMPLETE fixed Python code. Do not skip any parts."""
    else:
        user_prompt = f"""Generate a Manim scene for the following:

Scene ID: {scene.scene_id}
Title: {scene.title}
Description: {scene.description}
Plugin: {scene.plugin}
Visual elements: {', '.join(scene.visual_elements)}
Animations: {', '.join(scene.animations)}
Duration: {scene.duration_seconds}s

Generate complete, executable Python code. The scene class should be named Scene{scene.scene_id}."""

    response = client.chat.completions.create(
        model=CODEGEN_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4096,
        temperature=0.2,
    )

    code = response.choices[0].message.content

    # Extract code from markdown blocks if present
    code_match = re.search(r"```python\s*(.*?)```", code, re.DOTALL)
    if code_match:
        code = code_match.group(1)

    return code.strip()


def fix_scene_code(code: str, error: str, scene: SceneSpec) -> str:
    """Send failed code + error back to the model for fixing.

    Parameters
    ----------
    code : str
        The code that failed.
    error : str
        The error message from rendering.
    scene : SceneSpec
        Original scene specification.

    Returns
    -------
    str
        Fixed Python code.
    """
    client = _get_client()
    system = CODEGEN_SYSTEM_PROMPT or _default_codegen_system()

    user_prompt = f"""This Manim code failed to render. Fix it.

Original scene: {scene.title} - {scene.description}

Code:
```python
{code}
```

Error:
```
{error}
```

Return the COMPLETE fixed Python code. Preserve the scene class name."""

    response = client.chat.completions.create(
        model=CODEGEN_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4096,
        temperature=0.2,
    )

    fixed = response.choices[0].message.content
    code_match = re.search(r"```python\s*(.*?)```", fixed, re.DOTALL)
    if code_match:
        fixed = code_match.group(1)

    return fixed.strip()


def generate_all_scenes(scenes: list[SceneSpec]) -> dict[int, str]:
    """Generate code for all scenes.

    Returns
    -------
    dict[int, str]
        Mapping of scene_id -> generated code.
    """
    results = {}
    for scene in scenes:
        code = generate_scene_code(scene)
        results[scene.scene_id] = code
    return results


def _default_codegen_system() -> str:
    return """You are an expert Manim programmer. Convert scene descriptions into executable Manim Community Edition Python code.

Rules:
1. Always start with `from manim import *` and `from manim_banim import *`
2. Each scene is a class inheriting from Scene (or ThreeDScene for 3D content)
3. Use dark background (default). White/light text only.
4. Avoid overlapping elements. Use .to_edge(), .next_to(), .shift()
5. Add self.wait() between major animations for pacing
6. Keep animations smooth: use run_time=1-2s, lag_ratio for sequences
7. Clean up: FadeOut elements before introducing new ones when the screen gets crowded
8. Label everything. Use Text() with font_size 20-28 for readability.
9. Scene class name must match Scene{scene_id} format
10. Always output complete, runnable Python code

Available banim primitives:
- Nucleotide(base_type="A/T/G/C/U", sugar_type="deoxyribose/ribose")
- BasePair(left_base="A", right_base=None)  # auto-complements
- DNAStrand(sequence="ATCGATCG")
- DNADoubleHelix(sequence="ATCGATCG")  # has .unzip_anim(), .zip_anim()
- DNAHelix3D(n_turns=3, radius=1, pitch=0.5)  # for ThreeDScene
- MRNA(sequence="AUGCGA", show_cap=True, show_polya=True)
- TRNA(anticodon="UAC", amino_acid="Met")  # has .detach_aa_anim()
- Codon(sequence="AUG")
- AminoAcid(name="Ala")  # 20 standard amino acids
- PeptideChain(sequence=["Ala","Gly","Ser"])  # has .build_anim(), .fold_anim()
- AlphaHelix(), BetaSheet(), ProteinBlob(name="Protein")
- CellMembrane(width=6, n_lipids=12)
- Ribosome()  # has .assemble_anim(), .disassemble_anim()
- Cell(show_nucleus=True, show_er=True, show_mitochondria=True, show_ribosomes=True)
- Nucleus(), Mitochondrion()
- BioLabel(text, target, direction), LeaderLine(start, end), AnnotationBox(text)
- Color constants: ADENINE_COLOR, THYMINE_COLOR, GUANINE_COLOR, CYTOSINE_COLOR, URACIL_COLOR, etc.

Output only the Python code, no explanations."""
