import os
import subprocess
from moviepy.editor import VideoFileClip
import pygame

# 1. Download a YouTube video (clip of specific duration)
def download_youtube_clip(url, output_path, start_time, end_time):
    """
    Downloads a YouTube video and trims it to the specified time range using ffmpeg.
    - url: YouTube video URL
    - output_path: where to save the final clip (e.g., /home/pi/my_clip.mp4)
    - start_time, end_time: format 'HH:MM:SS' or seconds
    """
    temp_video = "temp_youtube_video.mp4"
    subprocess.run([
        "yt-dlp", "-f", "best[ext=mp4]", "-o", temp_video, url
    ])

    subprocess.run([
        "ffmpeg", "-ss", str(start_time), "-to", str(end_time),
        "-i", temp_video, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", output_path
    ])

    os.remove(temp_video)

# 2. Crop a video to portrait (7.5 x 13.5 aspect ratio)
def crop_to_portrait(input_path, output_path, target_width=720, target_height=1280):
    """
    Crops the video to a 9:16 portrait orientation.
    - input_path: path to the original video
    - output_path: path to save cropped video
    """
    clip = VideoFileClip(input_path)
    original_w, original_h = clip.size

    crop_width = int(original_h * 9 / 16)
    x_center = original_w // 2
    x1 = x_center - crop_width // 2
    x2 = x_center + crop_width // 2

    cropped = clip.crop(x1=x1, x2=x2)
    resized = cropped.resize((target_width, target_height))
    resized.write_videofile(output_path, codec='libx264')

# 3. Play video full screen

def play_video_fullscreen(video_path):
    """
    Plays a video full-screen using pygame.
    """
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

# Example usage (uncomment to run)
# download_youtube_clip("https://www.youtube.com/watch?v=EXAMPLE", "clip.mp4", "00:01:05", "00:01:35")
# crop_to_portrait("clip.mp4", "portrait_clip.mp4")
# play_video_fullscreen("portrait_clip.mp4")
