import requests
import time
import subprocess
import os

# Check if Next.js server is running on port 3002
def check_server():
    try:
        response = requests.get("http://localhost:3000/docs")
        if response.status_code == 200:
            print("✅ Server is running.")
            return True
    except requests.exceptions.RequestException:
        pass
    print("❌ Server is not running.")
    return False

# Start the server if it's not running
def start_server():
    print("🚀 Starting Next.js server...")
    subprocess.Popen(["cmd", "/c", "npm run dev"], cwd=os.getcwd(), shell=True)
    
    # Wait until the server starts (max wait: 30 seconds)
    max_wait = 30
    waited = 0
    while waited < max_wait:
        if check_server():
            return
        time.sleep(2)
        waited += 2
    print("❌ Server failed to start within the expected time.")

# Ensure the server is running before making requests
if not check_server():
    start_server()

# Define API base URL
BASE_URL = "http://localhost:3000/docs"

# Step 1: Custom generate the song
def generate_song(prompt, tags, title, make_instrumental=False, model=None, wait_audio=True, negative_tags=None):
    url = f"{BASE_URL}/custom_generate"
    payload = {
        "prompt": prompt,
        "tags": tags,
        "title": title,
        "make_instrumental": make_instrumental,
        "model": model,
        "wait_audio": wait_audio,
        "negative_tags": negative_tags
    }

    try:
        response = requests.post(url, json=payload)
        response_data = response.json() if response.status_code == 200 else None
        print(response.text)  # Show raw response

        if response.status_code == 200:
            song_id = response_data.get("id")
            print(f"✅ Song generation started: {song_id}")
            return song_id
        else:
            print(f"❌ Error: {response_data}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

# Step 2: Get the generated song details
def get_song(song_id, max_retries=10, delay=5):
    url = f"{BASE_URL}/get/{song_id}"  # FIXED API Endpoint

    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response_data = response.json() if response.status_code == 200 else None
            print(response.text)  # Show raw response

            if response.status_code == 200 and response_data:
                song_info = response_data[0]  # Assuming only one song ID was passed
                if song_info.get("status") == "complete":
                    print(f"🎵 Song ready: {song_info['audio_url']}")
                    return song_info
                else:
                    print(f"⏳ Attempt {attempt + 1}: Song still processing...")
            else:
                print(f"⚠️ Unexpected response: {response_data}")
        except Exception as e:
            print(f"❌ Error fetching song: {e}")

        time.sleep(delay)  # Wait before retrying

    print("❌ Failed to retrieve song after multiple attempts.")
    return None

# === Usage Example ===
prompt_text = "[Verse] The sky is blue and the wind is free..."
tags_list = "uplifting, orchestral"
song_title = "Sky Symphony"

# Step 1: Generate the song
generated_song_id = generate_song(prompt_text, tags_list, song_title)

# Step 2: Fetch the song details
if generated_song_id:
    song_details = get_song(generated_song_id)

    if song_details:
        print(f"✅ Download your song: {song_details['audio_url']}")
    else:
        print("❌ Song generation failed.")
