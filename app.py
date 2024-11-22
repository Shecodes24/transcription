from flask import Flask, request, jsonify
import os
import whisper
import moviepy.editor as mp
import numpy as np
import concurrent.futures
from pydub import AudioSegment
from pathlib import Path
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

def extract_audio_from_video(video_path):
    print(f"Extracting audio from {video_path}...")
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio_path = tempfile.mktemp(suffix=".wav")
    audio.write_audiofile(audio_path, codec='pcm_s16le') 
    print(audio_path)
    return audio_path

def split_audio(audio_path, chunk_duration_ms=60000):
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i+chunk_duration_ms]
        chunk_path = tempfile.mktemp(suffix=".wav")
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks

def transcribe_audio_chunk(chunk_path):
    try:
        model = whisper.load_model("base")
        print(f"Transcribing {chunk_path}...")
        result = model.transcribe(chunk_path)
        os.remove(chunk_path) 
        return result['text']
    except Exception as e:
        print(f"Error processing {chunk_path}: {e}")
        os.remove(chunk_path) 
        return "" 
    
def process_video_for_transcription(video_path):
    
    audio_path = extract_audio_from_video(video_path)
    audio_chunks = split_audio(audio_path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        transcriptions = list(executor.map(transcribe_audio_chunk, audio_chunks))
    full_transcription = " ".join(transcriptions)
    os.remove(audio_path)
    return full_transcription

# Default route
@app.route('/')
def home():
    return "Welcome to the simple Flask API!"

# Upload route
@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'video' not in request.files:
        return jsonify({"error": "No video file part"}), 400
    
    video_file = request.files['video']
    
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    video_path = os.path.join(tempfile.gettempdir(), video_file.filename)
    video_file.save(video_path)
    
    try:
        transcribed_text = process_video_for_transcription(video_path)
        print("function invoked")
        if transcribed_text:
            return jsonify({"message": f"Transcribed successfully, transcription is: {transcribed_text}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process the video: {str(e)}"}), 500
   
if __name__ == "__main__":
    app.run(debug=True)
