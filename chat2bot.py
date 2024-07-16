import openai
import sounddevice as sd
import numpy as np
import threading
import queue
import sys
import time
import os
from scipy.io.wavfile import write
from keypad_controller import KeypadController
from openai_key import get_key

# Set up your OpenAI API key
openai.api_key = get_key()

# Global variables
q = queue.Queue()
recording_event = threading.Event()

# Function to record audio
def record_audio(samplerate, channels):
    print("Recording... Press '*' to stop.")
    audio_data = []

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    stream = sd.InputStream(samplerate=samplerate, channels=channels, callback=callback)
    with stream:
        while recording_event.is_set():
            audio_data.append(q.get())
        stream.stop()

    return np.concatenate(audio_data, axis=0)

# Function to save audio to a WAV file
def save_audio_to_wav(audio_data, samplerate, filename):
    write(filename, samplerate, audio_data.astype(np.int16))

# Function to transcribe audio using OpenAI
def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = openai.Audio.transcribe(model="whisper-1", file=audio_file)
    return transcription['text']

# Function to interact with ChatGPT
def chat_with_gpt(transcribed_text):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": transcribed_text}],
        max_tokens=100
    )
    return completion.choices[0].message['content']

# Function to create speech using OpenAI's voice synthesis
def create_speech(text):
    response = openai.Audio.create(
        model="text-to-speech",
        input={"text": text},
        voice="default",  # or specify the desired voice if applicable
        response_format="wav"  # Ensure the correct audio format is used
    )

    audio_data = np.frombuffer(response['data'], dtype=np.int16)
    sd.play(audio_data, samplerate=44100)
    sd.wait()

# Function to process audio and interact with ChatGPT
def process_audio():
    samplerate = 44100  # Sample rate for recording
    channels = 1  # Number of audio channels

    audio_data = record_audio(samplerate, channels)
    wav_filename = "recording.wav"
    save_audio_to_wav(audio_data, samplerate, wav_filename)
    transcribed_text = transcribe_audio(wav_filename)
    print(f"Transcribed Text: {transcribed_text}")

    response_text = chat_with_gpt(transcribed_text)
    print(f"ChatGPT Response: {response_text}")

    create_speech(response_text)
    os.remove(wav_filename)  # Clean up the temporary file

# Function to handle keypad input
class KeypadListener:
    def __init__(self, controller):
        self.controller = controller
        self.recording_thread = None

    def key_pressed(self, key):
        print(key + " Pressed")
        if key == '*':
            if not recording_event.is_set():
                recording_event.set()
                print("Recording started.")
                self.recording_thread = threading.Thread(target=process_audio)
                self.recording_thread.start()

    def key_released(self, key):
        print(key + " Released")
        if key == '*':
            if recording_event is_set():
                recording_event.clear()
                print("Recording stopped.")
                if self.recording_thread is not None:
                    self.recording_thread.join()

def main():
    controller = KeypadController()
    listener = KeypadListener(controller)

    controller.key_pressed = listener.key_pressed
    controller.key_released = listener.key_released

    while True:
        controller.run()  # Start the keypad controller
        time.sleep(0.1)  # Small sleep to prevent high CPU usage

if __name__ == "__main__":
    main()
