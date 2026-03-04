"""Main orchestrator: runs all 6 stages end-to-end."""

import json
import os
import sys
import time
from pathlib import Path

from pipeline.config import OUTPUT_DIR, TEMP_DIR
from pipeline.stage1_extract import extract, ExtractedContent
from pipeline.stage2_planner import plan_scenes, ScenePlan
from pipeline.stage3_codegen import generate_all_scenes
from pipeline.stage4_render import render_all_scenes
from pipeline.stage5_tts import generate_all_voiceovers
from pipeline.stage6_assembly import assemble_video

__all__ = ["run_pipeline"]


def run_pipeline(
    source: str,
    output_dir: str | None = None,
    max_scenes: int = 10,
    enable_vision_qa: bool = False,
    enable_tts: bool = True,
    save_intermediate: bool = True,
) -> str:
    """Run the full paper-to-animation pipeline.

    Parameters
    ----------
    source : str
        Input source: PDF path, arXiv ID, or plain text topic.
    output_dir : str
        Directory for all outputs.
    max_scenes : int
        Maximum number of scenes.
    enable_vision_qa : bool
        Whether to run GPT-4o vision QA on renders.
    enable_tts : bool
        Whether to generate voiceovers.
    save_intermediate : bool
        Whether to save intermediate artifacts (plan JSON, code files).

    Returns
    -------
    str
        Path to the final video.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    print("=" * 60)
    print("BANIM: Paper-to-Animation Pipeline")
    print("=" * 60)

    # --- Stage 1: Extract ---
    print("\n[Stage 1/6] Extracting content...")
    t0 = time.time()
    content = extract(source)
    print(f"  Title: {content.title}")
    print(f"  Source type: {content.source_type}")
    print(f"  Sections: {len(content.sections)}")
    print(f"  Done in {time.time() - t0:.1f}s")

    # --- Stage 2: Plan ---
    print("\n[Stage 2/6] Planning scenes...")
    t0 = time.time()
    plan = plan_scenes(content, max_scenes=max_scenes)
    print(f"  Video title: {plan.video_title}")
    print(f"  Scenes: {len(plan.scenes)}")
    for s in plan.scenes:
        print(f"    Scene {s.scene_id}: {s.title} [{s.plugin}] ({s.duration_seconds}s)")
    print(f"  Total duration: {plan.total_duration:.0f}s")
    print(f"  Done in {time.time() - t0:.1f}s")

    if save_intermediate:
        plan_path = os.path.join(output_dir, "scene_plan.json")
        with open(plan_path, "w") as f:
            json.dump(plan.to_dict(), f, indent=2)
        print(f"  Plan saved: {plan_path}")

    # --- Stage 3: Generate code ---
    print("\n[Stage 3/6] Generating animation code...")
    t0 = time.time()
    scene_codes = generate_all_scenes(plan.scenes)
    print(f"  Generated {len(scene_codes)} scene files")
    print(f"  Done in {time.time() - t0:.1f}s")

    if save_intermediate:
        code_dir = os.path.join(output_dir, "code")
        os.makedirs(code_dir, exist_ok=True)
        for scene_id, code in scene_codes.items():
            code_path = os.path.join(code_dir, f"scene_{scene_id}.py")
            with open(code_path, "w") as f:
                f.write(code)

    # --- Stage 4: Render ---
    print("\n[Stage 4/6] Rendering scenes...")
    t0 = time.time()
    video_clips = render_all_scenes(
        scene_codes, plan.scenes,
        output_dir=TEMP_DIR,
        enable_vision_qa=enable_vision_qa,
    )
    print(f"  Rendered {len(video_clips)}/{len(plan.scenes)} scenes")
    print(f"  Done in {time.time() - t0:.1f}s")

    if not video_clips:
        print("\nERROR: No scenes rendered successfully. Aborting.")
        sys.exit(1)

    # --- Stage 5: TTS ---
    audio_clips = {}
    if enable_tts:
        print("\n[Stage 5/6] Generating voiceovers...")
        t0 = time.time()
        narrations = {s.scene_id: s.narration for s in plan.scenes if s.narration}
        audio_dir = os.path.join(output_dir, "audio")
        audio_clips = generate_all_voiceovers(narrations, audio_dir)
        print(f"  Generated {len(audio_clips)} audio clips")
        print(f"  Done in {time.time() - t0:.1f}s")
    else:
        print("\n[Stage 5/6] TTS skipped")

    # --- Stage 6: Assembly ---
    print("\n[Stage 6/6] Assembling final video...")
    t0 = time.time()
    final_path = os.path.join(output_dir, "final.mp4")
    result = assemble_video(
        video_clips=video_clips,
        audio_clips=audio_clips or None,
        video_title=plan.video_title,
        output_path=final_path,
    )
    print(f"  Done in {time.time() - t0:.1f}s")

    print("\n" + "=" * 60)
    print(f"DONE! Final video: {result}")
    print("=" * 60)

    return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Banim: Paper-to-Animation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m pipeline.pipeline "How mRNA vaccines work"
  python -m pipeline.pipeline 2301.12345
  python -m pipeline.pipeline paper.pdf
  python -m pipeline.pipeline "CRISPR-Cas9 gene editing" --max-scenes 8
        """,
    )
    parser.add_argument("source", help="PDF path, arXiv ID, or topic text")
    parser.add_argument("--output-dir", "-o", default=None, help="Output directory")
    parser.add_argument("--max-scenes", "-n", type=int, default=10, help="Max scenes")
    parser.add_argument("--vision-qa", action="store_true", help="Enable GPT-4o vision QA")
    parser.add_argument("--no-tts", action="store_true", help="Disable TTS voiceover")
    parser.add_argument("--no-save", action="store_true", help="Don't save intermediate files")

    args = parser.parse_args()

    run_pipeline(
        source=args.source,
        output_dir=args.output_dir,
        max_scenes=args.max_scenes,
        enable_vision_qa=args.vision_qa,
        enable_tts=not args.no_tts,
        save_intermediate=not args.no_save,
    )


if __name__ == "__main__":
    main()
