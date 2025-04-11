import whisper
import json
import os

"""This script is used to transcribe a song using the Whisper model and extract word timestamps and compare the resulting timestamps with the timestamps obttained from the api-endpoint, get_aligned_lyrics"""

# Load Whisper model
model = whisper.load_model("medium")

# Transcribe the song with word timestamps
audio_path = r"C:\Users\ozdep\Documents\social robotics final project\Social-Robotics-Practical\Assignment_3\src\suno_music\suno_repository\suno_api\saved_songs\API END POINT SONGS\Purrfect_Day.mp3"
result = model.transcribe(audio_path, word_timestamps=True)

# Print the raw output to see what's inside
print(json.dumps(result, indent=4))

# Extract timestamps for each word
word_timestamps = []
for segment in result.get("segments", []):  
    for word in segment.get("words", []):  
        if "text" in word and "start" in word and "end" in word:
            word_timestamps.append({
                "word": word["text"],
                "start": word["start"],
                "end": word["end"]
            })



# Target directory to save the JSON file
save_dir = r"C:\Users\ozdep\Documents\social robotics final project\Social-Robotics-Practical\Assignment_3\src\suno_music\suno_repository\suno_api\saved_songs\API END POINT SONGS"

# Make sure the directory exists
os.makedirs(save_dir, exist_ok=True)

# Full file path
output_path = os.path.join(save_dir, "word_timestamps.json")

# Save the word-level transcription result
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4)

print(f"Saved word timestamps to {output_path}")
