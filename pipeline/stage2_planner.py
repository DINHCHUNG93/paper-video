"""Stage 2: Scene planning using Claude."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import anthropic

from pipeline.config import ANTHROPIC_API_KEY, PLANNER_MODEL, PLUGIN_ROUTING
from pipeline.stage1_extract import ExtractedContent

__all__ = ["ScenePlan", "SceneSpec", "plan_scenes"]

PLANNER_SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "planner_system.txt").read_text() if (Path(__file__).parent.parent / "prompts" / "planner_system.txt").exists() else ""


@dataclass
class SceneSpec:
    """Specification for a single animation scene."""
    scene_id: int
    title: str
    description: str
    plugin: str  # "manim", "chanim", or "banim"
    visual_elements: list[str] = field(default_factory=list)
    animations: list[str] = field(default_factory=list)
    narration: str = ""
    duration_seconds: float = 10.0


@dataclass
class ScenePlan:
    """Full scene plan for a video."""
    video_title: str
    scenes: list[SceneSpec] = field(default_factory=list)
    total_duration: float = 0.0

    def to_dict(self) -> dict:
        return {
            "video_title": self.video_title,
            "total_duration": self.total_duration,
            "scenes": [
                {
                    "scene_id": s.scene_id,
                    "title": s.title,
                    "description": s.description,
                    "plugin": s.plugin,
                    "visual_elements": s.visual_elements,
                    "animations": s.animations,
                    "narration": s.narration,
                    "duration_seconds": s.duration_seconds,
                }
                for s in self.scenes
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ScenePlan":
        plan = cls(
            video_title=data["video_title"],
            total_duration=data.get("total_duration", 0),
        )
        for s in data["scenes"]:
            plan.scenes.append(SceneSpec(**s))
        if not plan.total_duration:
            plan.total_duration = sum(s.duration_seconds for s in plan.scenes)
        return plan


def _detect_plugin(description: str) -> str:
    """Auto-detect which plugin a scene should use based on keywords."""
    description_lower = description.lower()
    scores = {}
    for plugin, pattern in PLUGIN_ROUTING.items():
        matches = len(re.findall(pattern, description_lower, re.IGNORECASE))
        scores[plugin] = matches

    if max(scores.values()) == 0:
        return "manim"
    return max(scores, key=scores.get)


def plan_scenes(content: ExtractedContent, max_scenes: int = 10) -> ScenePlan:
    """Use Claude to create a scene-by-scene animation plan.

    Parameters
    ----------
    content : ExtractedContent
        Extracted paper/topic content.
    max_scenes : int
        Maximum number of scenes to plan.

    Returns
    -------
    ScenePlan
        Structured scene plan.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_prompt = f"""Create a scene-by-scene plan for an animated explainer video about:

{content.to_prompt_text()}

Requirements:
- Maximum {max_scenes} scenes
- Each scene focuses on ONE concept
- Scenes build on each other progressively
- Write narration for a curious non-expert audience (3Blue1Brown style)
- For each scene, specify the plugin: "manim" (math), "chanim" (chemistry), or "banim" (biology)
- Specify exact visual elements from the available primitives

Output as JSON with this schema:
{{
    "video_title": "string",
    "scenes": [
        {{
            "scene_id": 1,
            "title": "Scene title",
            "description": "Detailed description of what happens visually",
            "plugin": "manim|chanim|banim",
            "visual_elements": ["Nucleotide", "DNADoubleHelix", ...],
            "animations": ["Create", "FadeIn", "unzip_anim", ...],
            "narration": "What the narrator says during this scene",
            "duration_seconds": 10
        }}
    ]
}}"""

    system = PLANNER_SYSTEM_PROMPT or _default_system_prompt()

    response = client.messages.create(
        model=PLANNER_MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Parse JSON from response
    response_text = response.content[0].text

    # Extract JSON from potential markdown code blocks
    json_match = re.search(r"```(?:json)?\s*(.*?)```", response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response_text

    plan_data = json.loads(json_str)
    plan = ScenePlan.from_dict(plan_data)

    # Validate/override plugin detection
    for scene in plan.scenes:
        detected = _detect_plugin(scene.description + " ".join(scene.visual_elements))
        if scene.plugin not in ("manim", "chanim", "banim"):
            scene.plugin = detected

    return plan


def _default_system_prompt() -> str:
    return """You are a world-class science educator creating 3Blue1Brown-style animated explainer videos.

Given a scientific paper or topic, create a scene-by-scene plan for an animated video. Each scene should:
- Focus on ONE concept
- Build on the previous scene
- Specify exact visual elements from available libraries
- Include narration text written for a curious non-expert audience
- Specify which animation plugin to use: manim, chanim, or banim

Available banim primitives:
- Nucleotide(base_type="A/T/G/C/U")
- BasePair(left_base, right_base)
- DNADoubleHelix(sequence), DNAStrand(sequence)
- MRNA(sequence), TRNA(anticodon, amino_acid), Codon(sequence)
- AminoAcid(name), PeptideChain(sequence)
- Ribosome(), Cell(), CellMembrane(), Nucleus(), Mitochondrion()
- AlphaHelix(), BetaSheet(), ProteinBlob(name)
- TranscriptionScene(), TranslationScene(), ReplicationScene()
- BioLabel(text, target), AnnotationBox(text)

Available manim primitives:
- All standard: Circle, Square, Arrow, Text, MathTex, NumberPlane, Graph, Axes, etc.
- Animations: Create, Transform, FadeIn, FadeOut, Write, GrowFromCenter, etc.

Available chanim primitives:
- ChemWithName(chemfig_string, name)
- Chemical reactions and compound diagrams

Output structured JSON only. No extra commentary."""
