from flask import Flask, request, jsonify
from Components.YoutubeDownloader import download_youtube_video
from Components.Edit import extractAudio, crop_video
from Components.Transcription import transcribeAudio
from Components.LanguageTasks import GetHighlight
from Components.FaceCrop import crop_to_vertical, combine_videos
import os

app = Flask(__name__)

@app.route('/video', methods=['GET'])
def process_video():
    # Get the YouTube URL from the query parameter
    url = request.args.get('video')
    if not url:
        return jsonify({"error": "Missing video URL"}), 400
    
    # Download the YouTube video
    Vid = download_youtube_video(url)
    if not Vid:
        return jsonify({"error": "Unable to download the video"}), 500
    
    Vid = Vid.replace(".webm", ".mp4")
    print(f"Downloaded video and audio files successfully at {Vid}")
    
    # Extract audio from the video
    Audio = extractAudio(Vid)
    if not Audio:
        return jsonify({"error": "No audio file found"}), 500
    
    # Transcribe the audio
    transcriptions = transcribeAudio(Audio)
    if len(transcriptions) == 0:
        return jsonify({"error": "No transcriptions found"}), 500

    # Compile transcriptions and find highlights
    TransText = ""
    for text, start, end in transcriptions:
        TransText += f"{start} - {end}: {text}\n"

    start, stop = GetHighlight(TransText)
    if start == 0 and stop == 0:
        return jsonify({"error": "Error in getting highlight"}), 500
    
    # Process and combine videos
    Output = "Out.mp4"
    crop_video(Vid, Output, start, stop)
    cropped = "cropped.mp4"
    crop_to_vertical(Output, cropped)
    
    # Final output
    final_output = "Final.mp4"
    combine_videos(Output, cropped, final_output)
    
    # Assuming video is saved in a public directory for access
    video_url = f"{request.host_url}static/{final_output}"  # Adjust path as needed
    
    return jsonify({"video_url": video_url})

if __name__ == '__main__':
    app.run(debug=True)
