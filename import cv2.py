import os
import numpy as np
import moviepy.editor as mp
import speech_recognition as sr
from nltk.tokenize import sent_tokenize
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont

def check_file_accessibility(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"File is not readable (permission denied): {file_path}")
        return False
    return True

def calculate_segment_times(sentence_index, total_duration, num_segments):
    segment_duration = total_duration / num_segments
    start_time = sentence_index * segment_duration
    end_time = (sentence_index + 1) * segment_duration
    return start_time, min(end_time, total_duration)

def create_text_image(text, font_path='arial.ttf', fontsize=24, color='white', bg_color=None):
    font = ImageFont.truetype(font_path, fontsize)
    dummy_img = Image.new('RGB', (1, 1), bg_color)
    draw = ImageDraw.Draw(dummy_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    img = Image.new('RGBA', (text_width, text_height), bg_color)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=color)
    
    return img

video_path = 'C:\\Users\\joyme\\OneDrive\\Pictures\\Camera Roll\\WIN_20240620_20_54_07_Pro.mp4'

if not check_file_accessibility(video_path):
    print("Please check the file path and permissions.")
    exit(1)

try:
    video = mp.VideoFileClip(video_path)
except OSError as e:
    print(f"Error loading video file: {e}")
    print("Check if the file path is correct and if the file is accessible.")
    exit(1)

num_segments = 3
for i in range(num_segments):
    start_time, end_time = calculate_segment_times(i, video.duration, num_segments)
    segment_clip = video.subclip(start_time, end_time)
    
    segment_audio_path = f'segment_audio_{i + 1}.wav'
    segment_clip.audio.write_audiofile(segment_audio_path)
    
    recognizer = sr.Recognizer()
    audio_clip = sr.AudioFile(segment_audio_path)
    with audio_clip as source:
        audio = recognizer.record(source)
    
    try:
        transcript = recognizer.recognize_google(audio, show_all=True)
        if 'alternative' in transcript and len(transcript['alternative']) > 0:
            sentence = transcript['alternative'][0]['transcript']
        else:
            sentence = 'Audio not clear'
    except sr.UnknownValueError:
        sentence = 'Could not understand audio'
    except sr.RequestError as e:
        sentence = f'Request error: {e}'
    except Exception as e:
        sentence = f'Other error: {e}'
    
    print(f"Segment {i + 1} transcript: {sentence}")
    
    text_img = create_text_image(sentence)
    txt_clip = ImageClip(np.array(text_img)).set_duration(segment_clip.duration).set_position(('center', 'bottom'))
    
    video_with_text = CompositeVideoClip([segment_clip, txt_clip])
    gif_path = f'gif_sentence_{i + 1}.gif'
    video_with_text.write_gif(gif_path, fps=10, program='ffmpeg')
    print(f'GIF saved to {gif_path}')