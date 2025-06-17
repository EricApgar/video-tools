import os
import subprocess
import ffmpeg
import pygame

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
        "-f", "bestvideo+bestaudio",
        "--merge-output-format", "mp4",
        "-o", output_path,
        url
    ])

# 2. Crop a video to portrait (7.5 x 13.5 aspect ratio) using ffmpeg

def crop_to_portrait(input_path, output_path, target_width=720, target_height=1280):
    """
    Crops and resizes the video using ffmpeg-python to 9:16 portrait orientation.
    This avoids MoviePy dependency issues on Raspberry Pi.
    """
    probe = ffmpeg.probe(input_path)
    video_stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    original_w = int(video_stream['width'])
    original_h = int(video_stream['height'])

    crop_width = int(original_h * 9 / 16)
    x_offset = (original_w - crop_width) // 2

    (
        ffmpeg
        .input(input_path)
        .filter('crop', crop_width, original_h, x_offset, 0)
        .filter('scale', target_width, target_height)
        .output(output_path)
        .run()
    )

# 3. Play video full screen

def play_video_fullscreen_old(video_path):
    """
    Plays a video full-screen using pygame.
    """
    from moviepy import VideoFileClip

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    clip = VideoFileClip(video_path)
    for frame in clip.iter_frames(fps=24, dtype='uint8'):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                return

        surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        surface = pygame.transform.scale(surface, screen.get_size())
        screen.blit(surface, (0, 0))
        pygame.display.update()
        clock.tick(24)

    pygame.quit()


def play_video_fullscreen(video_path):
    subprocess.run(["mpv", "--fs", "--no-terminal", "--really-quiet", video_path])


# Example usage (uncomment to run)
# download_youtube_clip("https://www.youtube.com/watch?v=EXAMPLE", "clip.mp4", "00:01:05", "00:01:35")
# crop_to_portrait("clip.mp4", "portrait_clip.mp4")
# play_video_fullscreen("portrait_clip.mp4")


# Example usage (uncomment to run)
if __name__ == '__main__':
    download_youtube_clip("https://www.youtube.com/watch?v=zEvjBoDDp0M", "clip.mp4", "00:01:00", "00:01:30")
    crop_to_portrait("clip.mp4", "portrait_clip.mp4")
    play_video_fullscreen("portrait_clip.mp4")
