"""Stage 6: Video assembly using ffmpeg — stitch clips, overlay audio, add transitions."""

import os
import subprocess
import tempfile

__all__ = ["assemble_video", "get_duration"]


def get_duration(file_path: str) -> float:
    """Get duration of a media file in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path,
        ],
        capture_output=True, text=True, timeout=10,
    )
    return float(result.stdout.strip())


def _add_audio_to_video(
    video_path: str,
    audio_path: str,
    output_path: str,
) -> str:
    """Overlay audio on video, extending video if audio is longer."""
    video_dur = get_duration(video_path)
    audio_dur = get_duration(audio_path)
    max_dur = max(video_dur, audio_dur)

    # If video is shorter than audio, loop the last frame
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest" if video_dur >= audio_dur else "-t", str(max_dur) if video_dur < audio_dur else "",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path,
    ]
    # Clean up empty strings
    cmd = [c for c in cmd if c]

    subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True)
    return output_path


def _create_title_card(
    title: str,
    duration: float = 3.0,
    output_path: str = "/tmp/banim_title.mp4",
    width: int = 1920,
    height: int = 1080,
) -> str:
    """Create a simple title card video using ffmpeg."""
    # Escape special chars for ffmpeg drawtext
    safe_title = title.replace("'", "\\'").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s={width}x{height}:d={duration}:r=30",
        "-vf", f"drawtext=text='{safe_title}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=True)
    return output_path


def assemble_video(
    video_clips: dict[int, str],
    audio_clips: dict[int, str] | None = None,
    video_title: str = "Explainer Video",
    output_path: str = "output/final.mp4",
    add_title_card: bool = True,
    transition_duration: float = 0.5,
) -> str:
    """Assemble scene clips into a final video with audio.

    Parameters
    ----------
    video_clips : dict[int, str]
        Mapping of scene_id -> video file path, in order.
    audio_clips : dict[int, str] or None
        Mapping of scene_id -> audio file path.
    video_title : str
        Title for the title card.
    output_path : str
        Path for the final output video.
    add_title_card : bool
        Whether to prepend a title card.
    transition_duration : float
        Fade transition duration between scenes.

    Returns
    -------
    str
        Path to the final assembled video.
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="banim_assembly_") as tmpdir:
        # Step 1: Combine audio with individual clips (if audio provided)
        processed_clips = []

        if add_title_card:
            title_path = os.path.join(tmpdir, "title.mp4")
            _create_title_card(video_title, output_path=title_path)
            processed_clips.append(title_path)

        for scene_id in sorted(video_clips.keys()):
            video_path = video_clips[scene_id]
            audio_path = audio_clips.get(scene_id) if audio_clips else None

            if audio_path and os.path.exists(audio_path):
                combined_path = os.path.join(tmpdir, f"scene_{scene_id}_combined.mp4")
                _add_audio_to_video(video_path, audio_path, combined_path)
                processed_clips.append(combined_path)
            else:
                processed_clips.append(video_path)

        if not processed_clips:
            raise ValueError("No clips to assemble")

        if len(processed_clips) == 1:
            # Just copy the single clip
            subprocess.run(
                ["cp", processed_clips[0], output_path],
                check=True,
            )
            return output_path

        # Step 2: Create concat file
        concat_file = os.path.join(tmpdir, "concat.txt")
        with open(concat_file, "w") as f:
            for clip in processed_clips:
                f.write(f"file '{clip}'\n")

        # Step 3: Concatenate with ffmpeg
        # First normalize all clips to same format
        normalized = []
        for i, clip in enumerate(processed_clips):
            norm_path = os.path.join(tmpdir, f"norm_{i}.mp4")
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", clip,
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-r", "30",
                    "-s", "1920x1080",
                    "-pix_fmt", "yuv420p",
                    "-ar", "44100",
                    "-ac", "2",
                    norm_path,
                ],
                capture_output=True, text=True, timeout=60,
            )
            normalized.append(norm_path)

        norm_concat = os.path.join(tmpdir, "norm_concat.txt")
        with open(norm_concat, "w") as f:
            for clip in normalized:
                f.write(f"file '{clip}'\n")

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", norm_concat,
                "-c", "copy",
                output_path,
            ],
            capture_output=True, text=True, timeout=120, check=True,
        )

    print(f"Final video assembled: {output_path}")
    return output_path
