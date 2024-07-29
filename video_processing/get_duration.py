from moviepy.editor import VideoFileClip
import math

def get_duration(video_path:str) -> float:
    """
    Utility function to get duration of clip with it's path
    """
    video = VideoFileClip(video_path)
    duration = 100 * round(video.duration, 2)
    duration_rounded_up = 8 * math.ceil(duration / 8) 
    return duration_rounded_up