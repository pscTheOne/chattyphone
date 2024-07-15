# event_controller.py
import time
import openai
import sqlite3
#import pyttsx3
import threading
import socket
import pyaudio
from scipy.signal import resample
from controller import Controller  # Import the Controller class
from openai_key import get_key  # Import the get_key function

openai.api_key = get_key()

class EventController:
    def __init__(self):
        #self.stt_engine = pyttsx3.init()

        self.controller = Controller()
        ##self.controller.keypad_controller.key_released = self.keypad_key_released

        self.current_user_id = None
        self.last_interaction_time = time.time()
        self.phone_picked_up = False

        self.setup_audio_stream()

    def setup_audio_stream(self):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, frames_per_buffer=1024)

    def create_connection(self):
        conn = sqlite3.connect('conversations.db')
        return conn

    def load_conversation_history(self, user_id):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT history FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else ""

    def save_conversation(self, user_id, user_input, bot_response):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (user_id, history) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET history = history || ?",
                       (user_id, f"User: {user_input}\nChatGPT: {bot_response}\n", f"User: {user_input}\nChatGPT: {bot_response}\n"))
        conn.commit()
        conn.close()

    def get_chatbot_response(self, prompt, user_id):
        history = self.load_conversation_history(user_id)
        full_prompt = history + "\nUser: " + prompt + "\nChatGPT:"

        response = openai.Completion.create(
            model="gpt-4",
            prompt=full_prompt,
            max_tokens=150
        )
        response_text = response['choices'][0]['text']
        self.save_conversation(user_id, prompt, response_text)

        return response_text

    def speak_response(self, response):
        print("we should do some stuff here")
        #self.stt_engine.say(response)
        #self.stt_engine.runAndWait()

    def play_dtmf_tone(self, key):
        dtmf = DTMF(key)
        tone = dtmf.to_audio_segment(duration=300)
        play_obj = sa.play_buffer(tone.raw_data, num_channels=1, bytes_per_sample=2, sample_rate=44100)
        play_obj.wait_done()

    def handle_voice_input(self, transcription):
        self.last_interaction_time = time.time()  # Update the interaction time
        if transcription.lower().startswith("user id"):
            self.current_user_id = transcription.split()[-1]
            response = self.get_chatbot_response("User changed to " + self.current_user_id, self.current_user_id)
            self.speak_response(response)
        else:
            response = self.get_chatbot_response(transcription, self.current_user_id)
            self.speak_response(response)

    def keypad_key_pressed(self, key):
        self.last_interaction_time = time.time()  # Update the interaction time
        self.play_dtmf_tone(key)  # Play the DTMF tone for the pressed key
        if key == 'H':  # Receiver picked up
            self.phone_picked_up = True
            # self.current_user_id = None
            # response = self.get_chatbot_response("Hello! Please identify yourself.", self.current_user_id)
            # self.speak_response(response)
        elif key == '#':  # Assuming # is the submit key
            self.handle_keypad_submit()
        else:
            self.controller.keypad_key_pressed(key)

    def keypad_key_released(self, key):
        self.controller.keypad_key_released(key)

    def handle_keypad_submit(self):
        self.current_user_id = self.controller.get_keypad_input()[:-1]  # Use keypad input as user ID
        response = self.get_chatbot_response("User changed to " + self.current_user_id, self.current_user_id)
        self.speak_response(response)
        self.controller.reset_keypad_input()  # Reset the keypad input

    def ring_telephone(self):
        print("Ringing the telephone...")
        # Add code to ring the telephone (e.g., trigger a sound or LED)

    def stt_loop(self):
        while True:
            audio_data = self.stream.read(1024)
            self.send_audio_to_server(audio_data)

    def send_audio_to_server(self, audio_data):
        # Resample audio data from 48000 Hz to 16000 Hz
        resampled_audio = resample(audio_data, int(len(audio_data) * 16000 / 48000)).astype('int16')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("34.118.49.79", 43007))
            s.sendall(resampled_audio.tobytes())
            transcription = s.recv(1024).decode('utf-8')

        if transcription:
            self.handle_voice_input(transcription)

    def run(self):
        stt_thread = threading.Thread(target=self.stt_loop)
        stt_thread.daemon = True
        stt_thread.start()

        while True:
        #    if self.controller.detect_motion():
        #        self.last_interaction_time = self.controller.get_last_motion_time()

            self.controller.run_keypad()

            current_time = time.time()

        #    if current_time - self.last_interaction_time > 300:
        #        if self.controller.detect_motion():
        #            self.ring_telephone()
        #            self.current_user_id = None  # Reset user
        #            self.last_interaction_time = current_time

            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

# Usage
if __name__ == '__main__':
    event_controller = EventController()
    event_controller.run()
