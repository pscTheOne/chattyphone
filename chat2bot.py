import openai
import sounddevice as sd
import numpy as np
import threading
import queue
import sys
from keypad_controller import KeypadController
from openai_key import get_key
import time

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

# Function to transcribe audio using Whisper
def transcribe_audio(audio_data, samplerate):
    audio_base64 = openai.util.array_to_base64(audio_data, dtype="int16", shape=(len(audio_data), 1))
    response = openai.Audio.transcriptions.create(
        audio=audio_base64,
        model="whisper-1",
        encoding="pcm_s16le",
        sample_rate=samplerate
    )
    return response['text']

# Function to interact with ChatGPT
def chat_with_gpt(transcribed_text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=transcribed_text,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Function to create speech using OpenAI's voice synthesis
def create_speech(text):
    response = openai.Audio.create(
        model="voice-synthesis",
        text=text
    )
    audio_data = np.frombuffer(response["audio"], dtype=np.int16)
    sd.play(audio_data, samplerate=44100)
    sd.wait()

# Function to process audio and interact with ChatGPT
def process_audio():
    samplerate = 44100  # Sample rate for recording
    channels = 1  # Number of audio channels

    audio_data = record_audio(samplerate, channels)
    transcribed_text = transcribe_audio(audio_data, samplerate)
    print(f"Transcribed Text: {transcribed_text}")

    response_text = chat_with_gpt(transcribed_text)
    print(f"ChatGPT Response: {response_text}")

    create_speech(response_text)

# Function to handle keypad input
class KeypadListener:
    def __init__(self, controller):
        self.controller = controller

    def key_pressed(self, key):
        print(key + " Pressed")
        if key == '*':
            if not recording_event.is_set():
                recording_event.set()
                print("Recording started.")
                process_audio()

    def key_released(self, key):
        print(key + " Released")
        if key == '*':
            if recording_event.is_set():
                recording_event.clear()
                print("Recording stopped.")

def main():
    controller = KeypadController()
    listener = KeypadListener(controller)

    controller.key_pressed = listener.key_pressed
    controller.key_released = listener.key_released
    while True:
        sleep(1)
        pass


if __name__ == "__main__":
    main()
