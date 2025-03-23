import whisper
import json

# Load Whisper model
model = whisper.load_model("small")

# Transcribe the song with word timestamps
audio_path = r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\saved_songs\Purrfect_Day.mp3"
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

# Save to JSON
#with open("word_timestamps.json", "w") as f:
    #json.dump(word_timestamps, f, indent=4)

with open(r"C:\Users\ozdep\Documents\suno 1002\suno-api\suno-api\word_timestamps.json", "w") as f:
    json.dump(result, f, indent=4)

print("Saved word timestamps to word_timestamps.json.")
