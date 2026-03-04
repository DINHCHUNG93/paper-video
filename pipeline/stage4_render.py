"""Stage 4: Manim rendering with retry loop and optional vision QA."""

import base64
import glob
import os
import subprocess
import tempfile
from pathlib import Path

from openai import AzureOpenAI

from pipeline.config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
    VISION_MODEL,
    MANIM_QUALITY,
    MAX_RETRIES,
    RENDER_TIMEOUT,
    TEMP_DIR,
)
from pipeline.stage2_planner import SceneSpec
from pipeline.stage3_codegen import fix_scene_code

__all__ = ["render_scene", "render_all_scenes"]


class RenderError(Exception):
    """Raised when a scene fails to render after all retries."""
    pass


def _find_output_video(scene_name: str, media_dir: str) -> str | None:
    """Find the rendered video file in Manim's output directory."""
    patterns = [
        os.path.join(media_dir, "videos", "**", f"{scene_name}.mp4"),
        os.path.join(media_dir, "videos", "**", "*.mp4"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            # Return the most recently modified
            return max(matches, key=os.path.getmtime)
    return None


def _extract_frame(video_path: str, timestamp: float = 2.0) -> str | None:
    """Extract a frame from the video and return as base64."""
    frame_path = video_path.replace(".mp4", "_frame.png")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-ss", str(timestamp),
         "-frames:v", "1", frame_path],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode == 0 and os.path.exists(frame_path):
        with open(frame_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        os.remove(frame_path)
        return b64
    return None


def _vision_qa(video_path: str) -> tuple[bool, str]:
    """Use GPT-4o to evaluate a rendered frame for visual quality.

    Returns (pass, feedback).
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
        return True, "Vision QA skipped (no Azure OpenAI configured)"

    frame_b64 = _extract_frame(video_path)
    if not frame_b64:
        return True, "Could not extract frame, skipping QA"

    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version="2024-12-01-preview",
    )

    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a visual QA reviewer for Manim animations. Check for: overlapping text, elements off-screen, unreadable labels, visual glitches. Respond with PASS or FAIL followed by brief feedback.",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Review this animation frame for visual quality issues:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{frame_b64}"}},
                ],
            },
        ],
        max_tokens=200,
    )

    feedback = response.choices[0].message.content
    passed = feedback.strip().upper().startswith("PASS")
    return passed, feedback


def render_scene(
    code: str,
    scene: SceneSpec,
    output_dir: str | None = None,
    enable_vision_qa: bool = False,
) -> str:
    """Render a scene with retry loop.

    Parameters
    ----------
    code : str
        Python code for the scene.
    scene : SceneSpec
        Scene specification.
    output_dir : str
        Directory for output files.
    enable_vision_qa : bool
        Whether to run GPT-4o vision QA on rendered frames.

    Returns
    -------
    str
        Path to the rendered .mp4 file.

    Raises
    ------
    RenderError
        If rendering fails after MAX_RETRIES attempts.
    """
    if output_dir is None:
        output_dir = TEMP_DIR
    os.makedirs(output_dir, exist_ok=True)

    scene_name = f"Scene{scene.scene_id}"
    filepath = os.path.join(output_dir, f"scene_{scene.scene_id}.py")
    media_dir = os.path.join(output_dir, "media")

    current_code = code

    for attempt in range(MAX_RETRIES):
        # Write code
        with open(filepath, "w") as f:
            f.write(current_code)

        # Render
        result = subprocess.run(
            ["manim", MANIM_QUALITY, "--media_dir", media_dir, filepath, scene_name],
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT,
            cwd=output_dir,
        )

        if result.returncode == 0:
            video_path = _find_output_video(scene_name, media_dir)
            if video_path is None:
                error_msg = "Render succeeded but output video not found"
                current_code = fix_scene_code(current_code, error_msg, scene)
                continue

            if enable_vision_qa:
                passed, feedback = _vision_qa(video_path)
                if not passed:
                    current_code = fix_scene_code(
                        current_code,
                        f"Visual QA failed: {feedback}",
                        scene,
                    )
                    continue

            return video_path
        else:
            error = result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr
            print(f"  [Attempt {attempt + 1}/{MAX_RETRIES}] Render failed: {error[:200]}...")
            current_code = fix_scene_code(current_code, error, scene)

    raise RenderError(
        f"Scene {scene.scene_id} ({scene.title}) failed after {MAX_RETRIES} retries"
    )


def render_all_scenes(
    scene_codes: dict[int, str],
    scenes: list[SceneSpec],
    output_dir: str | None = None,
    enable_vision_qa: bool = False,
) -> dict[int, str]:
    """Render all scenes sequentially.

    Returns
    -------
    dict[int, str]
        Mapping of scene_id -> video file path.
    """
    results = {}
    for scene in scenes:
        code = scene_codes.get(scene.scene_id)
        if code is None:
            print(f"No code for scene {scene.scene_id}, skipping")
            continue

        print(f"Rendering scene {scene.scene_id}: {scene.title}...")
        try:
            video_path = render_scene(code, scene, output_dir, enable_vision_qa)
            results[scene.scene_id] = video_path
            print(f"  Scene {scene.scene_id} rendered: {video_path}")
        except RenderError as e:
            print(f"  FAILED: {e}")

    return results
