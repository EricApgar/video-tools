import os
import subprocess
import ffmpeg

# 1. Download a YouTube video (clip of specific duration) efficiently

def download_youtube_clip(url, output_path, start_time, end_time):
    """
    Downloads a specific clip from a YouTube video without downloading the full video.
    - url: YouTube video URL
    - output_path: where to save the final clip (e.g., /home/pi/my_clip.mp4)
    - start_time, end_time: format 'HH:MM:SS'
    """
    time_range = f"*{start_time}-{end_time}"
    subprocess.run([
        "yt-dlp",
        "--download-sections", time_range,
        "--force-keyframes-at-cuts",
        "-f", "bestvideo+bestaudio",  #"-f", "best[ext=mp4]",
        "--merge-output-format", "mp4",
        "-o", output_path,
        url
    ])

# 2. Crop a video to portrait (7.5 x 13.5 aspect ratio) using ffmpeg

def crop_to_portrait(input_path, output_path, target_width=1080, target_height=1920, crop_center=0.5):
    """
    Crops and resizes the video using ffmpeg-python to 9:16 portrait orientation.
    Allows horizontal adjustment via crop_center (0.0 = far left, 1.0 = far right).
    Re-encodes to H.264 MP4 at 30 FPS.
    """
    probe = ffmpeg.probe(input_path)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    original_w = int(video_stream['width'])
    original_h = int(video_stream['height'])

    crop_width = int(original_h * 9 / 16)
    crop_center = max(0.0, min(1.0, crop_center))  # Clamp to [0, 1]
    center_x = int(original_w * crop_center)
    x1 = center_x - crop_width // 2
    x1 = max(0, min(x1, original_w - crop_width))  # Ensure within bounds

    (
        ffmpeg
        .input(input_path)
        .filter('crop', crop_width, original_h, x1, 0)
        .filter('scale', target_width, target_height)
        .output(output_path, vcodec='libx264', r=30, acodec='aac', preset='fast')
        .run()
    )

# 3. Play video full screen using mpv

def play_video_fullscreen(video_path):
    """
    Plays a video full-screen using mpv for smooth hardware-accelerated playback.
    """
    subprocess.run(["mpv", "--fs", "--no-terminal", "--really-quiet", video_path])

# Example usage (uncomment to run)
# download_youtube_clip("https://www.youtube.com/watch?v=EXAMPLE", "clip.mp4", "00:01:05", "00:01:35")
# crop_to_portrait("clip.mp4", "portrait_clip.mp4", crop_center=0.25)
# play_video_fullscreen("portrait_clip.mp4")


# Example usage (uncomment to run)
if __name__ == '__main__':
    download_youtube_clip("https://www.youtube.com/watch?v=zEvjBoDDp0M", "clip.mp4", "00:01:00", "00:01:30")
    crop_to_portrait("clip.mp4", "portrait_clip.mp4", crop_center=.8)
    play_video_fullscreen("portrait_clip.mp4")
