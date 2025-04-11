import requests
import time
import subprocess
import os
import json

# Define API base URL (without /docs)
BASE_URL = "http://localhost:3000"
BASE_DIR = "suno-api"
SAVE_DIR = os.path.join(BASE_DIR, "saved_songs")


def check_server():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("Server is running.")
            return True
    except requests.exceptions.RequestException:
        pass
    print("Server is not running.")
    return False


def start_server():
    """Start the Next.js server if it's not running."""
    print(" Starting Next.js server...")
    subprocess.Popen(["cmd", "/c", "npm run dev"], cwd=os.getcwd(), shell=True)
    
    max_wait = 30
    waited = 0
    while waited < max_wait:
        if check_server():
            print(" Waiting 5 more seconds for endpoints to load...")
            time.sleep(5)
            return
        time.sleep(2)
        waited += 2
    print(" Server failed to start within the expected time.")


if not check_server():
    start_server()


def ensure_directory_exists(directory):
    """Ensure the specified directory exists; create it if not."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def sanitize_filename(filename):
    """Sanitize the filename by replacing invalid characters."""
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in filename).strip()


def save_lyrics(song_title, lyrics):
    """Save lyrics to a text file."""
    ensure_directory_exists(SAVE_DIR)
    filename = os.path.join(SAVE_DIR, f"{sanitize_filename(song_title)}.txt")

    with open(filename, "w", encoding="utf-8") as file:
        file.write(lyrics)
    print(f" Lyrics saved to: {filename}")
    return filename


def save_metadata(song_title, song_id, audio_url):
    """Save metadata (ID, audio URL) to a file."""
    ensure_directory_exists(SAVE_DIR)
    filename = os.path.join(SAVE_DIR, f"{sanitize_filename(song_title)}_metadata.txt")

    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Title: {song_title}\nID: {song_id}\nAudio URL: {audio_url}\n")
    print(f" Metadata saved to: {filename}")
    return filename


def download_audio(song_title, audio_url):
    """Download audio and save it."""
    if not audio_url or audio_url == "None":
        print(" No valid audio URL found. Skipping download.")
        return None

    ensure_directory_exists(SAVE_DIR)
    filename = os.path.join(SAVE_DIR, f"{sanitize_filename(song_title)}.mp3")

    try:
        response = requests.get(audio_url, stream=True)
        if response.status_code == 200:
            with open(filename, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Audio saved to: {filename}")
            return filename
        else:
            print(f"Failed to download audio: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None

def custom_generate(prompt, tags="playful, elementary school", negative_tags="female vocals", title=None, make_instrumental=False, model="chirp-v3-5|chirp-v3-0", wait_audio=False):
    """Generate a custom song with provided parameters."""
    url = f"{BASE_URL}/api/custom_generate"
    payload = {
        "prompt": prompt,
        "tags": tags,
        "negative_tags": negative_tags,
        "title": title,
        "make_instrumental": make_instrumental,
        "model": model,
        "wait_audio": wait_audio
    }

    try:
        response = requests.post(url, json=payload)
        response_data = response.json() if response.status_code == 200 else None

        if not response_data or not isinstance(response_data, list):
            print("Invalid response format from API.")
            return None

        songs = []
        for item in response_data:
            if isinstance(item, dict):
                inner_data = next(iter(item.values()), None)  # Extract first nested dictionary safely
                if isinstance(inner_data, dict):
                    song_id = inner_data.get("id")
                    title = inner_data.get("title")
                    lyrics = inner_data.get("lyric")
                    audio_url = inner_data.get("audio_url")

                    if song_id and title:
                        print(f"Song generated: {song_id}")

                        # Save lyrics if available
                        lyrics_file = save_lyrics(title, lyrics) if lyrics else None
                        metadata_file = save_metadata(title, song_id, audio_url) if audio_url else None
                        audio_file = download_audio(title, audio_url) if audio_url else None

                        songs.append({
                            "id": song_id, "title": title, "lyrics": lyrics or "No lyrics available",
                            "audio_url": audio_url or "No audio URL", "lyrics_file": lyrics_file,
                            "metadata_file": metadata_file, "audio_file": audio_file
                        })
                    else:
                        print(f"Missing essential song details: {inner_data}")

        return songs if songs else None

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def generate_song(prompt, make_instrumental=False, model="chirp-v3-5|chirp-v3-0", wait_audio=True):
    """Generate a song based on a prompt."""
    url = f"{BASE_URL}/api/generate/"
    payload = {"prompt": prompt, "make_instrumental": make_instrumental, "model": model, "wait_audio": wait_audio}

    try:
        response = requests.post(url, json=payload)
        response_data = response.json() if response.status_code == 200 else None

        if response_data:
            songs = []
            for item in response_data:
                if isinstance(item, dict):  
                    song_id = item.get("id")
                    title = item.get("title")
                    lyrics = item.get("lyric")
                    audio_url = item.get("audio_url")

                    if song_id and title and lyrics and audio_url:
                        print(f"Song generated: {song_id}")

                        lyrics_file = save_lyrics(title, lyrics)
                        metadata_file = save_metadata(title, song_id, audio_url)
                        audio_file = download_audio(title, audio_url)

                        songs.append({
                            "id": song_id, "title": title, "lyrics": lyrics, "audio_url": audio_url,
                            "lyrics_file": lyrics_file, "metadata_file": metadata_file, "audio_file": audio_file
                        })
            return songs if songs else None
        else:
            print("Error generating song.")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def save_aligned_lyrics(song_id, aligned_lyrics_data):
    """Save aligned lyrics data as a JSON file."""
    ensure_directory_exists(SAVE_DIR)
    filename = os.path.join(SAVE_DIR, f"{song_id}_aligned_lyrics.json")

    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(aligned_lyrics_data, file, indent=4, ensure_ascii=False)
        print(f"Aligned lyrics saved to: {filename}")
        return filename
    except Exception as e:
        print(f"Error saving aligned lyrics: {e}")
        return None


def get_aligned_lyrics(song_id):
    """Fetch aligned lyrics from the API."""
    url = f"{BASE_URL}/api/get_aligned_lyrics/"
    params = {'song_id': song_id}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            aligned_lyrics_data = response.json()
            print(f"Aligned lyrics retrieved for {song_id}")
            return save_aligned_lyrics(song_id, aligned_lyrics_data)
        print("Aligned lyrics not found.")
    except Exception as e:
        print(f"Error fetching aligned lyrics: {e}")


# ===  Usage Example if you do not have predefined lyrics===
prompt_text = "A playful song about cats for Dutch kids aged 7-8 learning English."
song_data = generate_song(prompt_text)
if song_data:
    song_id = song_data[0]["id"]
    get_aligned_lyrics(song_id)
    print("DONE!")



