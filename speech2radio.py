import socket
import time
import threading
import requests

# Configuration
WHISPER_SERVER_IP = '34.118.49.79'
WHISPER_SERVER_PORT = 43007
MUSIC_GENERATION_SERVER = 'http://your-music-generation-server-address/generate'
RECORDING_DURATION = 120  # 2 minutes

transcribed_text = []

def record_and_transcribe():
    global transcribed_text
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((WHISPER_SERVER_IP, WHISPER_SERVER_PORT))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        s.listen(1)
        print(f'Listening on port {s.getsockname()[1]} for arecord...')

        # Start recording and send audio to the socket
        arecord_cmd = f'arecord -f S16_LE -c1 -r 16000 -t raw -D default | nc 127.0.0.1 {s.getsockname()[1]}'
        arecord_process = subprocess.Popen(arecord_cmd, shell=True)

        conn, addr = s.accept()
        with conn:
            print(f'Connected by {addr}')
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                sock.sendall(data)
                output = sock.recv(1024)
                if output:
                    transcribed_text.append(output.decode('utf-8').strip())

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
    transcribe_thread = threading.Thread(target=record_and_transcribe)
    transcribe_thread.daemon = True
    transcribe_thread.start()

    generate_song()
