import requests
import json
import time
from datetime import datetime

TRANSCRIPTION_URL = "http://34.118.49.79:5000/transcriptions"
GENERATION_URL = "http://192.168.1.27:5000/generate"

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
        "method": "prompt",
        "prompt": " ".join(keywords)
    }
    try:
        response = requests.post(GENERATION_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if result and 'song_id' in result:
            print(f"Song generation submitted. Song ID: {result['song_id']}")
        else:
            print(f"Failed to generate song: {result.get('error', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"Error generating song: {e}")

def main():
    while True:
        print(f"Fetching transcriptions at {datetime.now()}")
        transcriptions = fetch_transcriptions()
        if transcriptions:
            keywords = extract_keywords(transcriptions)
            if keywords:
                print(f"Generating song with keywords: {keywords}")
                generate_song(keywords)
            else:
                print("No keywords extracted from transcriptions.")
        else:
            print("No transcriptions fetched.")

        time.sleep(120)  # Sleep for 2 minutes

if __name__ == "__main__":
    main()
