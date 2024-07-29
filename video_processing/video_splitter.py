import os
from moviepy.editor import VideoFileClip

def split_video(video, part_durations, output_dir):
    """
    Split video into parts with custom durations and save to disk.
    """
    duration = video.duration

    # Check if the sum of part durations exceeds the video duration
    if sum(part_durations) > duration:
        raise ValueError("The sum of part durations exceeds the total duration of the video.")

    clips = []
    start_time = 0.0

    for i, part_duration in enumerate(part_durations):
        end_time = start_time + part_duration
        if end_time > duration:
            end_time = duration  # Ensure the clip does not exceed the video duration

        # Save each clip
        clip_path = os.path.join(output_dir, f"clip_{i+1}.mp4")
        subclip = video.subclip(start_time, end_time)
        subclip.write_videofile(clip_path, codec='libx264', audio_codec='aac')

        clips.append(clip_path)
        start_time = end_time  # Update start time for next clip

    return clips


