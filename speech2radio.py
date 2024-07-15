import socket
import time
import threading
import requests
import pyaudio

# Configuration
WHISPER_SERVER_IP = '34.118.49.79'
WHISPER_SERVER_PORT = 43007
MUSIC_GENERATION_SERVER = 'http://192.168.1.26:5000/generate'  # Assuming the server runs on port 5000
RECORDING_DURATION = 120  # 2 minutes
CHUNK = 960  # 960 samples per chunk to fit with rate
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

transcribed_text = []

def record_and_transcribe():
    global transcribed_text
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((WHISPER_SERVER_IP, WHISPER_SERVER_PORT))

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording...")

    try:
        while True:
            data = stream.read(CHUNK)
            sock.sendall(data)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Stopping recording...")
        stream.stop_stream()
        stream.close()
        p.terminate()
        sock.close()

def generate_song():
    global transcribed_text
    while True:
        time.sleep(RECORDING_DURATION)
        if transcribed_text:
            collected_text = ' '.join(transcribed_text)
            data = {
                'method': 'prompt',
                'prompt': collected_text
            }
            response = requests.post(MUSIC_GENERATION_SERVER, json=data)
            if response.status_code == 202:
                print(f"Song generation started. Song ID: {response.json().get('song_id')}")
            else:
                print(f"Error generating song: {response.json().get('error')}")
            transcribed_text = []

if __name__ == "__main__":
    try:
        transcribe_thread = threading.Thread(target=record_and_transcribe)
        transcribe_thread.daemon = True
        transcribe_thread.start()

        generate_song()
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
