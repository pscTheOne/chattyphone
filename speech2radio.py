import requests
import json
import time
from datetime import datetime

TRANSCRIPTION_URL = "http://34.118.49.79:5000/transcriptions"
SONG_GENERATION_URL = "https://api.sunoaiapi.com/api/v1/gateway/generate/gpt_desc"
SONG_STATUS_URL = "https://api.sunoaiapi.com/api/v1/gateway/query"
SONG_STREAM_URL = "https://api.sunoaiapi.com/api/v1/stream"
API_KEY = "VCwrNNJ1msu3dOQmGr46AM3WLxoecqLl"  # Replace with your actual API key

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
    return keywords[:10]  # Limit to 10 keywords

def generate_song(keywords):
    payload = {
        "gpt_description_prompt": " ".join(keywords)
    }
    try:
        response = requests.post(SONG_GENERATION_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        if result['code'] == 0 and 'data' in result:
            return result['data'][0]['song_id']
        else:
            print(f"Failed to generate song: {result.get('msg', 'Unknown error')}")
            print(result)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error generating song: {e}")
        return None

def check_song_status(song_id):
    try:
        response = requests.get(f"{SONG_STATUS_URL}?ids={song_id}", headers=headers)
        response.raise_for_status()
        result = response.json()
        if 'data' in result and result['data']:
            song_data = result['data'][0]
            return song_data.get('status') == 'streaming', song_data.get('audio_url')
        else:
            print(f"Song status data not available: {result}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"Error checking song status: {e}")
        return False, None

def stream_song(audio_url):
    try:
        print(f"Streaming song from {audio_url}")
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
                    song_ready, audio_url = False, None
                    while not song_ready:
                        print(f"Checking status of song ID: {song_id}")
                        song_ready, audio_url = check_song_status(song_id)
                        time.sleep(30)  # Check every 30 seconds
                    if audio_url:
                        stream_song(audio_url)
                else:
                    print("Failed to generate song.")
            else:
                print("No keywords extracted from transcriptions.")
        else:
            print("No transcriptions fetched.")

        time.sleep(120)  # Sleep for 2 minutes

if __name__ == "__main__":
    main()
