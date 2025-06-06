import tkinter as tk
import os
import pyttsx3
import pyautogui
import speech_recognition as sr
from tkinter import scrolledtext, simpledialog, messagebox
import threading
import google.generativeai as genai
import webbrowser
import time
import re
import requests
import yt_dlp
from PIL import ImageTk
import math
import colorsys
import logging
import random
import functools
# For cloud and multi-user (example: Firebase, AWS, or your own API)
import firebase_admin
from firebase_admin import credentials, firestore

# --- Self-healing and retry decorators ---
def self_healing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return "Error occurred. Please try again or contact support."
    return wrapper

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts < max_attempts:
                        print(f"Attempt {attempts} failed. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        return f"Operation failed after {max_attempts} attempts: {e}"
        return wrapper
    return decorator

@retry(max_attempts=3, delay=1)
def simulate_unstable_operation():
    if random.random() < 0.5:
        raise Exception("Operation failed")
    else:
        return "Operation succeeded"

class VirtualAssistant:
    """A scalable, multi-user, cloud-enabled, AI-powered voice assistant."""

    # Constants
    WINDOW_WIDTH = 900  # Optimized for mobile/tablet screens
    WINDOW_HEIGHT = 600
    PULSE_MAX_RADIUS_FACTOR = 0.25
    PULSE_MIN_RADIUS_FACTOR = 0.3
    PULSE_SPEED = 2
    ANIMATION_DELAY_MS = 10
    SPEECH_RATE = 150
    SPEECH_VOLUME = 1
    LISTENING_TIMEOUT = 5
    PHRASE_TIME_LIMIT = 5

    def __init__(self, master):
        self.master = master
        self.master.title("Rose")
        self.master.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.master.configure(bg="#181c24")
        self.master.resizable(True, True)
        self.root = master
        self.canvas = tk.Canvas(self.master, width=self.WINDOW_WIDTH, height=250, bg="#181c24", highlightthickness=0)
        self.canvas.pack(fill="x")
        self.pulse_radius = 80
        self.pulse_direction = 1
        self.angle = 0
        self.sphere_radius = 80
        self.num_slices = 30
        self.num_meridians = 30
        self.animation_speed = 10
        self.rotation_angle_y = 0
        self.rotation_speed_y = 0.02
        self.rotation_angle_x = 0
        self.rotation_speed_x = 0.01
        self.focal_length = 400
        self.center_x = self.canvas.winfo_width() / 2
        self.center_y = self.canvas.winfo_height() / 2
        self.voice_react_timer = 0
        self.voice_react_duration = 20
        self.animate_combined()
        self.languages = {"English": "en-US", "Hindi": "hi-IN"}
        self.listening = True
        self.last_gemini_response = None
        self.current_user = None  # For multi-user

        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.SPEECH_RATE)
        self.engine.setProperty('volume', self.SPEECH_VOLUME)
        # Try to set a soft, smooth female English voice
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if ("female" in voice.name.lower() or "zira" in voice.name.lower() or "eva" in voice.name.lower()) and "english" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

        # Configure Google Generative AI
        GOOGLE_API_KEY = "AIzaSyBla75QrCuFRBHQSXEjrfJUSLEcVY7TlA4"
        genai.configure(api_key=GOOGLE_API_KEY)
        self.chat_model = genai.GenerativeModel("gemini-2.0-flash")
        self.chat_session = self.chat_model.start_chat()

        # --- Cloud/Multi-user setup (stub) ---
        if not firebase_admin._apps:
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.user_id = None

        # UI Components
        self.create_ui()

        # Greet and guide on startup
        greeting = (
            "Hello, I am Rose, your virtual assistant. "
            "You can ask me to open apps, search the web, take notes, and more. "
            "Say 'help' to hear what I can do."
        )
        self.text_to_speech(greeting)
        self.chat_window.insert(tk.END, "Rose: Hello! Say 'help' to hear what I can do.\n\n")

        # System check
        result = simulate_unstable_operation()
        self.chat_window.insert(tk.END, f"System check: {result}\n\n")
        self.text_to_speech(f"System check: {result}")

        self.voice_listening()

    # --- Animation methods (unchanged, but optimized for smaller canvas) ---
    def rotate_point_3d(self, x, y, z, angle_x, angle_y):
        rotated_x = x * math.cos(angle_y) - z * math.sin(angle_y)
        rotated_z = x * math.sin(angle_y) + z * math.cos(angle_y)
        x, z = rotated_x, rotated_z
        rotated_y = y * math.cos(angle_x) - z * math.sin(angle_x)
        rotated_z = y * math.sin(angle_x) + z * math.cos(angle_x)
        y, z = rotated_y, rotated_z
        return x, y, z

    def project_3d_to_2d(self, x, y, z):
        perspective_factor = self.focal_length / (self.focal_length + z)
        proj_x = x * perspective_factor
        proj_y = y * perspective_factor
        return proj_x, proj_y

    def get_color_from_depth(self, z, max_z, base_hue):
        z_norm = (z + max_z) / (2 * max_z)
        lightness = 0.3 + (0.7 * z_norm)
        saturation = 0.6 + (0.4 * z_norm)
        r, g, b = colorsys.hls_to_rgb(base_hue / 360, lightness, saturation)
        return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"

    def animate_combined(self):
        self.center_x = self.canvas.winfo_width() / 2
        self.center_y = self.canvas.winfo_height() / 2
        self.canvas.delete("all")
        pulse_boost = 1.0
        color_boost = 0
        if self.voice_react_timer > 0:
            pulse_boost = 1.3
            color_boost = 80
            self.voice_react_timer -= 1
        canvas_width = self.master.winfo_width()
        canvas_height = 250
        center_x, center_y = canvas_width // 2, canvas_height // 2
        max_radius = min(canvas_width, canvas_height) * self.PULSE_MAX_RADIUS_FACTOR * pulse_boost
        min_radius = max_radius * self.PULSE_MIN_RADIUS_FACTOR
        self.pulse_radius += self.pulse_direction * self.PULSE_SPEED
        if self.pulse_radius > max_radius or self.pulse_radius < min_radius:
            self.pulse_direction *= -1
        pulse_color = "#00FFFF" if color_boost == 0 else "#%02XFFFF" % (0 + color_boost)
        for i in range(10, 0, -1):
            r = self.pulse_radius * (i / 10)
            self.canvas.create_oval(
                center_x - r, center_y - r,
                center_x + r, center_y + r,
                outline=pulse_color, width=2 if i == 10 else 1
            )
        self.canvas.create_oval(
            center_x - 30, center_y - 30,
            center_x + 30, center_y + 30,
            fill="#00ffff", outline=""
        )
        self.angle = (self.angle + 8) % 360
        self.rotation_angle_y += self.rotation_speed_y
        self.rotation_angle_x += self.rotation_speed_x
        self.root.after(self.animation_speed, self.animate_combined)

    # --- UI and Assistant Logic ---
    def create_ui(self):
        # Responsive layout for mobile/tablet
        chat_frame = tk.Frame(self.master, bg="#222b3a")
        chat_frame.place(relx=0.5, rely=0.65, anchor="center", width=self.WINDOW_WIDTH-40, height=220)
        self.chat_window = scrolledtext.ScrolledText(
            chat_frame,
            bg="#222b3a",
            fg="#e6e6e6",
            wrap=tk.WORD,
            font=("Arial", 13),
            borderwidth=2,
            relief=tk.RAISED,
            highlightthickness=2,
            highlightbackground="#00ffff",
            highlightcolor="#00ffff"
        )
        self.chat_window.pack(expand=True, fill="both", pady=(5, 0))
        input_frame = tk.Frame(self.master, bg="#181c24")
        input_frame.place(relx=0.5, rely=0.93, anchor="center", width=self.WINDOW_WIDTH-40, height=40)
        self.input_field = tk.Entry(
            input_frame,
            bg="#f0f0f0",
            font=("Arial", 13),
            borderwidth=2,
            relief=tk.GROOVE,
            highlightthickness=2,
            highlightbackground="#00ffff",
            highlightcolor="#00ffff"
        )
        self.input_field.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        send_button = tk.Button(input_frame, text="Send", command=self.send_manual_message, font=("Arial", 12), bg="#00b894", fg="white")
        send_button.pack(side="right", padx=5, pady=5)

        # Control Buttons (right of input)
        control_frame = tk.Frame(self.master, bg="#181c24")
        control_frame.place(relx=0.98, rely=0.93, anchor="e")
        stop_button = tk.Button(
            control_frame, text="Stop Speaking", command=self.stop_speaking,
            font=("Arial", 10), bg="red", fg="white", width=12, height=1
        )
        stop_button.pack(pady=2)

        # Language and filename
        self.language_var = tk.StringVar(value="English")
        language_option_menu = tk.OptionMenu(self.master, self.language_var, *self.languages.keys())
        language_option_menu.config(font=("Arial", 12), bg="#181c24", fg="#00ffff")
        language_option_menu.place(x=20, y=20)
        self.filename_area = tk.Text(self.master, bg="#ffeaa7", width=20, height=1, font=("Arial", 12))
        self.filename_area.place(x=180, y=20)
        self.filename_area.insert(tk.END, "voice_notes.txt")

        # --- Multi-user login (stub) ---
        login_button = tk.Button(self.master, text="Login", command=self.login_user, font=("Arial", 10), bg="#0984e3", fg="white")
        login_button.place(x=self.WINDOW_WIDTH-100, y=20)

        # --- Cloud sync button (stub) ---
        sync_button = tk.Button(self.master, text="Sync Cloud", command=self.sync_cloud, font=("Arial", 10), bg="#fdcb6e", fg="black")
        sync_button.place(x=self.WINDOW_WIDTH-200, y=20)

    def login_user(self):
        # Example: simple dialog for username (replace with real auth)
        username = simpledialog.askstring("Login", "Enter your username:")
        if username:
            self.current_user = username
            self.chat_window.insert(tk.END, f"Logged in as {username}\n")
            self.text_to_speech(f"Welcome, {username}!")
        else:
            self.chat_window.insert(tk.END, "Login cancelled.\n")

    def sync_cloud(self):
        # Stub: Replace with real cloud sync logic
        self.chat_window.insert(tk.END, "Syncing with cloud...\n")
        self.text_to_speech("Syncing with cloud.")
        # Example: Save chat to cloud or load from cloud
        if self.current_user:
            self.db.collection("users").document(self.current_user).set({"chat": self.chat_window.get("1.0", tk.END)})
            self.text_to_speech("Your chat has been saved to the cloud.")

    def send_manual_message(self):
        user_input = self.input_field.get().strip()
        if not user_input:
            self.text_to_speech("Please enter something to send.")
            return
        self.chat_window.insert(tk.END, f"You (Manual): {user_input}\n")
        self.input_field.delete(0, tk.END)
        self.process_command(user_input.lower())
        if not self.is_direct_command(user_input.lower()):
            response_text = self.get_response_from_gemini(user_input)
            self.chat_window.insert(tk.END, f"Bot: {response_text}\n\n")
            self.text_to_speech(self.clean_tts_text(response_text))
        self.text_to_speech("What would you like to do next?")

    def get_filename(self):
        filename = self.filename_area.get("1.0", tk.END).strip()
        return filename if filename else "voice_notes.txt"

    @self_healing
    @retry(max_attempts=3, delay=2)
    def get_response_from_gemini(self, user_input):
        try:
            # --- Advanced AI: context, persona, etc. ---
            context = f"User: {user_input}\nRose (AI):"
            response = self.chat_session.send_message(context)
            response_text = response.text
            self.last_gemini_response = response_text
            return response_text
        except Exception as e:
            print(f"Error getting response from Gemini: {e}")
            self.last_gemini_response = None
            return "Sorry, I couldn't connect to the AI model."

    def text_to_speech(self, text):
        try:
            selected_language = self.language_var.get()
            voices = self.engine.getProperty('voices')
            voice_found = False
            # Always use soft female if available
            for voice in voices:
                if ("female" in voice.name.lower() or "zira" in voice.name.lower() or "eva" in voice.name.lower()) and "english" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    voice_found = True
                    break
            if not voice_found:
                if selected_language == "Hindi":
                    for voice in voices:
                        if "hindi" in voice.name.lower() or "hi" in voice.id.lower():
                            self.engine.setProperty('voice', voice.id)
                            voice_found = True
                            break
                else:
                    for voice in voices:
                        if "english" in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            voice_found = True
                            break
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in text_to_speech: {e}")

    def take_voice(self, language, filename="voice_notes.txt"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        while True:
            if not self.listening:
                while not self.listening:
                    with mic as source:
                        self.text_to_speech("Listening is paused. Say 'start listening'")
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        try:
                            audio = recognizer.listen(source, timeout=self.LISTENING_TIMEOUT, phrase_time_limit=self.PHRASE_TIME_LIMIT)
                            command = recognizer.recognize_google(audio, language=language).lower()
                            if "start listening" in command:
                                self.listening = True
                                self.text_to_speech("Listening resumed.")
                                break
                        except sr.UnknownValueError:
                            pass
                        except sr.WaitTimeoutError:
                            pass
                        except Exception as e:
                            print(f"Error during paused listening: {e}")
                continue
            try:
                with mic as source:
                    self.text_to_speech("I am Listening")
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=self.LISTENING_TIMEOUT, phrase_time_limit=self.PHRASE_TIME_LIMIT)
                    command = recognizer.recognize_google(audio, language=language).lower()
                    print(f"You said: {command}")
                    self.text_to_speech(f"You said: {command}")
                    voice_input = command.strip().lower()
                    self.chat_window.insert(tk.END, f"You (Voice): {voice_input}\n")
                    self.input_field.delete(0, tk.END)
                    self.input_field.insert(0, voice_input)
                    if not voice_input:
                        self.text_to_speech("I didn't catch that. Please say your command again.")
                        continue
                    self.voice_react_timer = self.voice_react_duration
                    self.process_command(command)
                    if not self.is_direct_command(command):
                        response_text = self.get_response_from_gemini(command)
                        self.chat_window.insert(tk.END, f"Bot: {response_text}\n\n")
                        self.text_to_speech(self.clean_tts_text(response_text))
                    self.text_to_speech("What would you like to do next?")
            except sr.UnknownValueError:
                self.text_to_speech("Sorry, I didn't catch that. Please repeat your command.")
            except sr.RequestError as e:
                self.text_to_speech(f"Could not request results from speech recognition service; {e}")
            except sr.WaitTimeoutError:
                self.text_to_speech("Listening timed out. Say 'start listening' to activate me.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.text_to_speech("An unexpected error occurred.")

    def set_filename(self, filename):
        filename = filename.strip()
        if not filename.lower().endswith(".txt"):
            filename += ".txt"
        self.filename_area.delete("1.0", tk.END)
        self.filename_area.insert(tk.END, filename)
        self.text_to_speech(f"Filename set to {filename}. Please dictate your notes or command.")
        return filename if filename else "voice_notes.txt"

    def view_notes(self):
        filename = self.get_filename()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                content = file.read()
                self.chat_window.insert(tk.END, f"Notes in {filename}:\n{content}\n\n")
                self.text_to_speech(f"Displaying notes from {filename}.")
        else:
            self.chat_window.insert(tk.END, f"File '{filename}' not found.\n\n")
            self.text_to_speech("File not found.")
        self.text_to_speech("What would you like to do next?")
        return

    def delete_notes(self):
        filename = self.get_filename()
        if os.path.exists(filename):
            os.remove(filename)
            self.chat_window.insert(tk.END, f"Notes in '{filename}' deleted successfully.\n\n")
            self.text_to_speech("Notes deleted successfully.")
        else:
            self.chat_window.insert(tk.END, f"File '{filename}' not found.\n\n")
            self.text_to_speech("File not found.")
        self.text_to_speech("What would you like to do next?")
        return

    def speak_help(self):
        help_text = (
            "You can say: open notepad, play music, save file name followed by your filename, "
            "save file, view notes, delete notes, search something on Google, or play a song on YouTube. "
            "Say exit to close me. What would you like to do?"
        )
        self.text_to_speech(help_text)
        self.chat_window.insert(tk.END, f"Bot: {help_text}\n\n")

    def is_direct_command(self, command):
        app_commands = self._get_app_commands()
        close_commands = self._get_close_commands()
        system_commands = self._get_system_commands()
        assistant_commands = self._get_assistant_commands()
        for keyword in ["open", "start", "launch", "run", "execute", "play", "use", "access", "go to", "browse", "visit", "search", "find", "show", "display", "activate"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in app_commands:
                    return True
        for keyword in ["close", "exit", "quit", "stop", "terminate", "end"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in close_commands:
                    return True
        if command.startswith("play ") and command.endswith(" on youtube"):
            return True
        if command.startswith("search ") and command.endswith(" on google"):
            return True
        if command in system_commands:
            return True
        if command in assistant_commands:
            return True
        return False
    
    def _get_app_commands(self):
        return {
            "notepad": ("notepad.exe", "Opening Notepad."),
            "calculator": ("calc.exe", "Opening Calculator."),
            "file explorer": ("explorer.exe", "Opening File Explorer."),
            "command prompt": ("cmd.exe", "Opening Command Prompt."),
            "task manager": ("taskmgr.exe", "Opening Task Manager."),
            "gmail": ("start chrome https://mail.google.com", "Opening Gmail."),
            "youtube": ("start chrome https://www.youtube.com", "Opening YouTube."),
            "google": ("start chrome https://www.google.com", "Opening Google."),
            "facebook": ("start chrome https://www.facebook.com", "Opening Facebook."),
            "twitter": ("start chrome https://www.twitter.com", "Opening Twitter."),
            "whatsapp": ("start chrome https://web.whatsapp.com", "Opening WhatsApp."),
            "instagram": ("start chrome https://www.instagram.com", "Opening Instagram."),
            "linkedin": ("start chrome https://www.linkedin.com", "Opening LinkedIn."),
            "stack overflow": ("start chrome https://stackoverflow.com", "Opening Stack Overflow."),
            "github": ("start chrome https://github.com", "Opening GitHub."),
            "reddit": ("start chrome https://www.reddit.com", "Opening Reddit."),
            "quora": ("start chrome https://www.quora.com", "Opening Quora."),
            "amazon": ("start chrome https://www.amazon.com", "Opening Amazon."),
            "flipkart": ("start chrome https://www.flipkart.com", "Opening Flipkart."),
            "news": ("start chrome https://news.google.com", "Opening News."),
            "weather": ("start chrome https://weather.com", "Opening Weather."),
            "calendar": ("start outlookcal:", "Opening Calendar."),
            "clock": ("start ms-clock:", "Opening Clock."),
            "settings": ("start ms-settings:", "Opening Settings."),
            "control panel": ("control", "Opening Control Panel."),
            "chrome": ("start chrome", "Opening Google Chrome."),
            "firefox": ("start firefox", "Opening Mozilla Firefox."),
            "edge": ("start msedge", "Opening Microsoft Edge."),
            "safari": ("start safari", "Opening Safari."),
            "opera": ("start opera", "Opening Opera."),
            "brave": ("start brave", "Opening Brave."),
            "vivaldi": ("start vivaldi", "Opening Vivaldi."),
            "internet explorer": ("start iexplore", "Opening Internet Explorer."),
            "task scheduler": ("taskschd.msc", "Opening Task Scheduler."),
            "snipping tool": ("snippingtool", "Opening Snipping Tool."),
            "paint": ("mspaint", "Opening Paint."),
            "word": ("start winword", "Opening Microsoft Word."),
            "excel": ("start excel", "Opening Microsoft Excel."),
            "powerpoint": ("start powerpnt", "Opening Microsoft PowerPoint."),
            "access": ("start msaccess", "Opening Microsoft Access."),
            "publisher": ("start mspub", "Opening Microsoft Publisher."),
            "onenote": ("start onenote", "Opening Microsoft OneNote."),
            "teams": ("start teams", "Opening Microsoft Teams."),
            "skype": ("start skype", "Opening Skype."),
            "zoom": ("start zoom", "Opening Zoom."),
            "discord": ("start discord", "Opening Discord."),
            "slack": ("start slack", "Opening Slack."),
            "notepad++": ("start notepad++.exe", "Opening Notepad++."),
            "sublime text": ("start sublime_text.exe", "Opening Sublime Text."),
            "visual studio": ("start devenv", "Opening Visual Studio."),
            "eclipse": ("start eclipse", "Opening Eclipse."),
            "pycharm": ("start pycharm", "Opening PyCharm."),
            "intellij": ("start idea", "Opening IntelliJ IDEA."),
            "android studio": ("start studio64", "Opening Android Studio."),
            "apache netbeans": ("start netbeans", "Opening Apache NetBeans."),
            "next track": ("nircmd mediaplay next", "Skipping to the next track."),
            "previous track": ("nircmd mediaplay prev", "Going back to the previous track."),
            "play music": ("start wmplayer", "Opening Windows Media Player."),
            "pause music": ("nircmd mediaplay pause", "Pausing music playback."),
            "voice access": (lambda: pyautogui.hotkey("win", "h"), "Opening voice access mode."),
            "music": ("nircmd mediaplay stop", "Stopping music playback."),
        }

    def _get_close_commands(self):
        return {
            "notepad": ("taskkill /f /im notepad.exe", "Closing Notepad."),
            "calculator": ("taskkill /f /im calc.exe", "Closing Calculator."),
            "file explorer": ("taskkill /f /im explorer.exe", "Closing File Explorer."),
            "command prompt": ("taskkill /f /im cmd.exe", "Closing Command Prompt."),
            "chrome": ("taskkill /f /im chrome.exe", "Closing Google Chrome."),
            "firefox": ("taskkill /f /im firefox.exe", "Closing Mozilla Firefox."),
            "edge": ("taskkill /f /im msedge.exe", "Closing Microsoft Edge."),
            "safari": ("taskkill /f /im safari.exe", "Closing Safari."),
            "opera": ("taskkill /f /im opera.exe", "Closing Opera."),
            "brave": ("taskkill /f /im brave.exe", "Closing Brave."),
            "vivaldi": ("taskkill /f /im vivaldi.exe", "Closing Vivaldi."),
            "internet explorer": ("taskkill /f /im iexplore.exe", "Closing Internet Explorer."),
            "task scheduler": ("taskkill /f /im taskschd.msc", "Closing Task Scheduler."),
            "task manager": ("taskkill /f /im taskmgr.exe", "Closing Task Manager."),
            "gmail": ("taskkill /f /im chrome.exe", "Closing Gmail."), # Closes all chrome instances
            "youtube": ("taskkill /f /im chrome.exe", "Closing YouTube."), # Closes all chrome instances
            "google": ("taskkill /f /im chrome.exe", "Closing Google."), # Closes all chrome instances
            "facebook": ("taskkill /f /im chrome.exe", "Closing Facebook."), # Closes all chrome instances
            "twitter": ("taskkill /f /im chrome.exe", "Closing Twitter."), # Closes all chrome instances
            "whatsapp": ("taskkill /f /im chrome.exe", "Closing WhatsApp."), # Closes all chrome instances
            "instagram": ("taskkill /f /im chrome.exe", "Closing Instagram."), # Closes all chrome instances
            "linkedin": ("taskkill /f /im chrome.exe", "Closing LinkedIn."), # Closes all chrome instances
            "stack overflow": ("taskkill /f /im chrome.exe", "Closing Stack Overflow."), # Closes all chrome instances
            "github": ("taskkill /f /im chrome.exe", "Closing GitHub."), # Closes all chrome instances
            "reddit": ("taskkill /f /im chrome.exe", "Closing Reddit."), # Closes all chrome instances
            "quora": ("taskkill /f /im chrome.exe", "Closing Quora."), # Closes all chrome instances
            "amazon": ("taskkill /f /im chrome.exe", "Closing Amazon."), # Closes all chrome instances
            "flipkart": ("taskkill /f /im chrome.exe", "Closing Flipkart."), # Closes all chrome instances
            "news": ("taskkill /f /im chrome.exe", "Closing News."), # Closes all chrome instances
            "weather": ("taskkill /f /im chrome.exe", "Closing Weather."), # Closes all chrome instances
            "calendar": ("taskkill /f /im outlook.exe", "Closing Calendar."),
            "clock": ("taskkill /f /im Time.exe", "Closing Clock."),
            "settings": ("taskkill /f /im SystemSettings.exe", "Closing Settings."),
            "control panel": ("taskkill /f /im control.exe", "Closing Control Panel."),
            "task scheduler": ("taskkill /f /im mmc.exe", "Closing Task Scheduler."),
            "snipping tool": ("taskkill /f /im SnippingTool.exe", "Closing Snipping Tool."),
            "paint": ("taskkill /f /im mspaint.exe", "Closing Paint."),
            "word": ("taskkill /f /im WINWORD.EXE", "Closing Microsoft Word."),
            "excel": ("taskkill /f /im EXCEL.EXE", "Closing Microsoft Excel."),
            "powerpoint": ("taskkill /f /im POWERPNT.EXE", "Closing Microsoft PowerPoint."),
            "access": ("taskkill /f /im MSACCESS.EXE", "Closing Microsoft Access."),
            "publisher": ("taskkill /f /im MSPUB.EXE", "Closing Microsoft Publisher."),
            "onenote": ("taskkill /f /im ONENOTE.EXE", "Closing Microsoft OneNote."),
            "teams": ("taskkill /f /im Teams.exe", "Closing Microsoft Teams."),
            "skype": ("taskkill /f /im Skype.exe", "Closing Skype."),
            "zoom": ("taskkill /f /im Zoom.exe", "Closing Zoom."),
            "discord": ("taskkill /f /im Discord.exe", "Closing Discord."),
            "slack": ("taskkill /f /im slack.exe", "Closing Slack."),
            "notepad++": ("taskkill /f /im notepad++.exe", "Closing Notepad++."),
            "sublime text": ("taskkill /f /im sublime_text.exe", "Closing Sublime Text."),
            "visual studio": ("taskkill /f /im devenv.exe", "Closing Visual Studio."),
            "eclipse": ("taskkill /f /im eclipse.exe", "Closing Eclipse."),
            "pycharm": ("taskkill /f /im pycharm64.exe", "Closing PyCharm."),
            "intellij": ("taskkill /f /im idea64.exe", "Closing IntelliJ IDEA."),
            "android studio": ("taskkill /f /im studio64.exe", "Closing Android Studio."),
            "apache netbeans": ("taskkill /f /im netbeans64.exe", "Closing Apache NetBeans."),
        }

    def _get_system_commands(self):
        return {
            "restart the system": ("shutdown /r /t 5", "Restarting the system."),
            "shutdown the system": ("shutdown /s /t 5", "Shutting down the system."),
            "lock the system": ("rundll32.exe user32.dll,LockWorkStation", "Locking the system."),
            "sleep the system": ("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", "Putting the system to sleep."),
            "hibernate the system": ("rundll32.exe powrprof.dll,SetSuspendState 1,1,0", "Hibernating the system."),
            "log off": ("shutdown /l", "Logging off the current user."),
        }

    def _get_assistant_commands(self):
        return {
            "view notes": (self.view_notes, "Notes is opened"),
            "delete notes": (self.delete_notes, "Notes is deleted"),
            "save the chat": (self.save_last_gemini_response, "Gemini response saved to file"),  # <-- Add this line
            "clear chat": (lambda: self.chat_window.delete(1.0, tk.END), "Chat cleared"),
            "help": (self.speak_help, "Here are some things you can ask me."),
            "exit the app": (lambda: self.master.quit(), "Exiting the app."),
        }

    def process_command(self, command):
        app_commands = self._get_app_commands()
        close_commands = self._get_close_commands()
        system_commands = self._get_system_commands()
        assistant_commands = self._get_assistant_commands()
        for keyword in ["open", "start", "launch", "run", "execute", "play", "use", "access", "go to", "browse", "visit", "search", "find", "show", "display", "activate"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in app_commands:
                    action, response = app_commands[app_name]
                    if callable(action):
                        action()
                    else:
                        os.system(action)
                    self.text_to_speech(response)
                    self.text_to_speech("What would you like to do next?")
                    return
        for keyword in ["close", "exit", "quit", "stop", "terminate", "end"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in close_commands:
                    action, response = close_commands[app_name]
                    os.system(action)
                    self.text_to_speech(response)
                    self.text_to_speech("What would you like to do next?")
                    return
        if command in assistant_commands:
            action, response = assistant_commands[command]
            action()
            self.text_to_speech(response)
            self.text_to_speech("What would you like to do next?")
            return
        if command.startswith("play ") and command.endswith(" on youtube"):
            song_query = command[len("play "):-len(" on youtube")].strip()
            if song_query:
                query = song_query.replace(" ", "+")
                search_url = f"https://www.youtube.com/results?search_query={query}"
                try:
                    response = requests.get(search_url)
                    video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                    if video_ids:
                        video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                        self.text_to_speech(f"Playing {song_query} on YouTube.")
                        self.listening = False
                        try:
                            ydl_opts = {'quiet': True, 'skip_download': True, 'force_generic_extractor': True}
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                info = ydl.extract_info(video_url, download=False)
                                duration = info.get('duration', 0)
                        except Exception as e:
                            print(f"Error getting video duration with yt-dlp: {e}")
                            duration = 0
                        webbrowser.open(video_url)
                        if duration > 0:
                            time.sleep(duration + 5)
                        else:
                            time.sleep(180)
                        self.listening = True
                        self.text_to_speech("Song finished. I'm listening again.")
                    else:
                        self.text_to_speech("Sorry, I couldn't find that song on YouTube.")
                except Exception as e:
                    print(f"Error playing YouTube video: {e}")
                    self.text_to_speech("Sorry, I encountered an issue playing that on YouTube.")
            else:
                self.text_to_speech("Please tell me what song to play on YouTube.")
            self.text_to_speech("What would you like to do next?")
            return
        if command.startswith("save file name "):
            file = command[len("save file name "):].strip()
            if file:
                self.set_filename(file)
                text = self.input_field.get().strip()
                if text:
                    filename = self.get_filename()
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(text + "\n")
                    self.chat_window.insert(tk.END, f"Text saved to {filename}.\n\n")
                    self.text_to_speech(f"Text saved to {filename}.")
                else:
                    self.chat_window.insert(tk.END, "No text to save.\n\n")
                    self.text_to_speech("No text to save.")
            else:
                self.text_to_speech("Please provide a filename.")
            self.text_to_speech("What would you like to do next?")
            return
        if command.startswith("search ") and command.endswith(" on google"):
            search_query = command[len("search "):-len(" on google")].strip()
            if search_query:
                self.text_to_speech(f"Searching Google for {search_query}.")
                query = search_query.replace(" ", "+")
                url = f"https://www.google.com/search?q={query}"
                webbrowser.open(url)
                self.text_to_speech(f"Searching for {search_query} on Google.")
            else:
                self.text_to_speech("Please tell me what to search for on Google.")
            self.text_to_speech("What would you like to do next?")
            return
        if command in system_commands:
            action, response = system_commands[command]
            os.system(action)
            self.text_to_speech(response)
            self.text_to_speech("What would you like to do next?")
            return

    def voice_listening(self):
        language = self.languages[self.language_var.get()]
        threading.Thread(
            target=self.take_voice,
            args=(language,),
            daemon=True
        ).start()

    def save_last_gemini_response(self):
        if self.last_gemini_response:
            filename = self.get_filename()
            with open(filename, "a", encoding="utf-8") as file:
                file.write(self.clean_tts_text(self.last_gemini_response) + "\n")
            self.chat_window.insert(tk.END, f"Gemini response saved to {filename}.\n\n")
            self.text_to_speech(f"Gemini response saved to {filename}.")
        else:
            self.chat_window.insert(tk.END, "No Gemini response to save.\n\n")
            self.text_to_speech("No Gemini response to save.")
        self.text_to_speech("What would you like to do next?")

    def clean_tts_text(self, text):
        """Remove asterisks and extra whitespace for TTS clarity."""
        return text.replace("*", "").strip()

    def stop_speaking(self):
        try:
            self.engine.stop()
            self.text_to_speech("Speaking stopped.")
        except Exception as e:
            print(f"Error stopping speech: {e}")

    def start_listening(self):
        if not self.listening:
            self.listening = True
            self.text_to_speech("Listening and speaking resumed.")
        else:
            self.text_to_speech("Already listening and speaking.")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualAssistant(root)
    root.mainloop()