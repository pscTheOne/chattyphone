import requests
import json
import time
from datetime import datetime

TRANSCRIPTION_URL = "http://34.118.49.79:5000/transcriptions"
SONG_GENERATION_URL = "https://api.sunoaiapi.com/api/v1/gateway/generate/gpt_desc"
SONG_STATUS_URL = "https://api.sunoaiapi.com/api/v1/gateway/query"
SONG_STREAM_URL = "https://api.sunoaiapi.com/api/v1/stream"
API_KEY = "mPc7Fke/LMcJnYqR1+6Z+9nOQDEHV+tA"  # Replace with your actual API key

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

def fetch_transcriptions():
    try:
        response = requests.get(TRANSCRIPTION_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transcriptions: {e}")
        return []

def extract_keywords(transcriptions):
    keywords = []
    for transcription in transcriptions:
        parts = transcription.split()
        if len(parts) > 2:
            sentence = " ".join(parts[2:])
            keywords.extend(sentence.split())
    return keywords

def generate_song(keywords):
    payload = {
        "gpt_description_prompt": " ".join(str(keywords[1,9]))
    }
    try:
        response = requests.post(SONG_GENERATION_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if 'song_id' in result:
            return result['song_id']
        else:
            print(f"Failed to generate song: {result.get('error', 'Unknown error')}")
            print(result)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error generating song: {e}")
        return None

def check_song_status(song_id):
    try:
        payload = {
            "song_id": song_id
        }
        response = requests.post(SONG_STATUS_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get('status') == 'ready'
    except requests.exceptions.RequestException as e:
        print(f"Error checking song status: {e}")
        return False

def stream_song(song_id):
    try:
        stream_url = f"{SONG_STREAM_URL}/{song_id}"
        print(f"Streaming song from {stream_url}")
        # Code to handle streaming the song, e.g., opening the URL in a media player
    except Exception as e:
        print(f"Error streaming song: {e}")

def main():
    while True:
        print(f"Fetching transcriptions at {datetime.now()}")
        transcriptions = fetch_transcriptions()
        if transcriptions:
            keywords = extract_keywords(transcriptions)
            if keywords:
                print(f"Generating song with keywords: {keywords}")
                song_id = generate_song(keywords)
                if song_id:
                    print(f"Generated song with ID: {song_id}")
                    while not check_song_status(song_id):
                        print(f"Checking status of song ID: {song_id}")
                        time.sleep(30)  # Check every 30 seconds
                    stream_song(song_id)
                else:
                    print("Failed to generate song.")
            else:
                print("No keywords extracted from transcriptions.")
        else:
            print("No transcriptions fetched.")

        time.sleep(120)  # Sleep for 2 minutes

if __name__ == "__main__":
    main()
