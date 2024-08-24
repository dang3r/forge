import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
import multiprocessing

def create_text_clip(text, font_size, color, position, duration):
    return TextClip(text, fontsize=font_size, color=color, font='Arial', method='label') \
        .set_position(position).set_duration(duration)

def resize_preserve_aspect_ratio(clip, target_height):
    aspect_ratio = clip.w / clip.h
    target_width = int(target_height * aspect_ratio)
    return clip.resize(height=target_height).resize(width=target_width)

def process_video(video_file, exercise, target_height):
    video = VideoFileClip(video_file)
    
    # Resize video if it's larger than target height, preserving aspect ratio
    if video.h > target_height:
        video = resize_preserve_aspect_ratio(video, target_height)
    
    # Create exercise text
    exercise_text = create_text_clip(f"{exercise['name']} - {exercise['weight']}lbs x {exercise['reps']} reps",
                                     font_size=30, color='white', position=('center', 'bottom'), duration=video.duration)
    
    # Combine video and text
    return CompositeVideoClip([video, exercise_text])

def edit_workout_video(video_folder, output_file, title, exercises, target_height=720):
    # Load video files
    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith('.mp4')]
    video_files.sort()  # Ensure files are in order

    # Process videos sequentially
    clips = [process_video(video_file, exercise, target_height) 
             for video_file, exercise in zip(video_files, exercises)]

    # Find the maximum width among all clips
    max_width = max(clip.w for clip in clips)

    # Resize all clips to the maximum width (this ensures all clips have the same dimensions)
    clips = [clip.resize(width=max_width) for clip in clips]

    # Concatenate all clips
    final_video = concatenate_videoclips(clips)

    # Add title at the beginning
    title_clip = create_text_clip(title, font_size=50, color='white', position=('center', 'top'), duration=5)
    final_video = CompositeVideoClip([final_video, title_clip])

    # Write output file
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', 
                                threads=multiprocessing.cpu_count()) 
# Example usage
video_folder = 'videos'
output_file = 'workout_compilation1.mp4'
title = "2024-08-16 dcardoza - lifting notes - block 11 - Week 3 Day 2" 
exercises = [
    {"name": "Leg Press", "weight": 425, "reps": 10},
    {"name": "Leg Press", "weight": 425, "reps": 10},
]

edit_workout_video(video_folder, output_file, title, exercises)