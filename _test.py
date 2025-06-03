import tkinter as tk
import os
from numpy import save
import pyttsx3
import pyautogui
import speech_recognition as sr
from tkinter import scrolledtext
import threading
import google.generativeai as genai
import webbrowser
import time
import re
import requests
import yt_dlp
from PIL import Image, ImageTk
import math
import colorsys


 # Replace with your actual key

# Ensure you have the required libraries installed:
# pip install pyttsx3 pyautogui SpeechRecognition google-generativeai requests yt-dlp Pillow


class _test: # Virtual Assistant copy
    """A simple voice assistant GUI application."""

    # Constants
    WINDOW_WIDTH = 1500
    WINDOW_HEIGHT = 1000
    PULSE_MAX_RADIUS_FACTOR = 0.25
    PULSE_MIN_RADIUS_FACTOR = 0.3 # 30% of max radius
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

        self.master.configure(bg="black")
        self.master.resizable(False, False)
        self.root = master
        self.canvas = tk.Canvas(master, width=1000, height=1000, bg="black")
        self.canvas.pack()

        self.canvas = tk.Canvas(self.master, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT, bg="black", highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.pulse_radius = 150
        self.pulse_direction = 1
        self.angle = 0
        self.sphere_radius = 150
        self.num_slices = 40  # Increased for smoother appearance
        self.num_meridians = 40 # Increased for smoother appearance
        self.animation_speed = 10 # milliseconds per frame

        self.rotation_angle_y = 0 # Y-axis rotation
        self.rotation_speed_y = 0.02 # radians per frame (slightly slower)

        self.rotation_angle_x = 0 # X-axis rotation
        self.rotation_speed_x = 0.01 # radians per frame

        self.focal_length = 600 # For perspective projection. Adjust as needed.

        # Ensure center_x and center_y are set after canvas is packed and has its size
        self.center_x = self.canvas.winfo_width() / 2
        self.center_y = self.canvas.winfo_height() / 2

        # self.animate()
        # self.animate_jarvis()
        self.animate_combined()

        self.languages = {"English": "en-US", "Hindi": "hi-IN"}
        self.listening = True

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', self.SPEECH_RATE)
        self.engine.setProperty('volume', self.SPEECH_VOLUME)

        # Configure Google Generative AI
        # It's recommended to store API keys in environment variables
        # For example, set GOOGLE_API_KEY=YOUR_API_KEY in your system environment
        # and then access it like: os.getenv("GOOGLE_API_KEY")
        # For demonstration, keeping it here but strongly advise against it for production
        GOOGLE_API_KEY = "AIzaSyBla75QrCuFRBHQSXEjrfJUSLEcVY7TlA4"
        # Replace with your actual key or os.getenv
        genai.configure(api_key=GOOGLE_API_KEY)
        self.chat_model = genai.GenerativeModel("gemini-2.0-flash")
        self.chat_session = self.chat_model.start_chat()


        # UI Components
        self.create_ui()
        self.voice_listening()
    
    def rotate_point_3d(self, x, y, z, angle_x, angle_y):
        # Rotate around Y-axis
        rotated_x = x * math.cos(angle_y) - z * math.sin(angle_y)
        rotated_z = x * math.sin(angle_y) + z * math.cos(angle_y)
        x, z = rotated_x, rotated_z

        # Rotate around X-axis
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

        # Vary lightness and saturation based on depth for a richer effect
        lightness = 0.3 + (0.7 * z_norm)  # Ranges from 0.3 (darker) to 1.0 (brighter)
        saturation = 0.6 + (0.4 * z_norm)  # Ranges from 0.6 to 1.0 (more vibrant)

        r, g, b = colorsys.hls_to_rgb(base_hue / 360, lightness, saturation)
        return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
    
    def animate_combined(self):
    # Clear canvas once per frame
        self.center_x = self.canvas.winfo_width() / 2
        self.center_y = self.canvas.winfo_height() / 2
        self.canvas.delete("all")

    # --- Draw Jarvis pulse animation ---
        canvas_width = self.master.winfo_width()
        canvas_height = self.master.winfo_height()
        if canvas_width == 1:
            canvas_width = self.WINDOW_WIDTH
            canvas_height = self.WINDOW_HEIGHT
        center_x, center_y = canvas_width // 2, canvas_height // 2
        max_radius = min(canvas_width, canvas_height) * self.PULSE_MAX_RADIUS_FACTOR
        min_radius = max_radius * self.PULSE_MIN_RADIUS_FACTOR
        self.pulse_radius += self.pulse_direction * self.PULSE_SPEED
        if self.pulse_radius > max_radius or self.pulse_radius < min_radius:
            self.pulse_direction *= -1
        for i in range(10, 0, -1):
            r = self.pulse_radius * (i / 10)
            self.canvas.create_oval(
               center_x - r, center_y - r,
                center_x + r, center_y + r,
                outline="#00FFFF", width=2 if i == 10 else 1
            )
        for lat in range(-60, 80, 30):
            r_lat = self.pulse_radius * math.cos(math.radians(lat))
            self.canvas.create_oval(
                center_x - r_lat, center_y - r_lat * math.sin(math.radians(lat)),
                center_x + r_lat, center_y + r_lat * math.sin(math.radians(lat)),
                outline="#00FFFF", width=1
            )
        for lon in range(0, 180, 30):
            angle = math.radians(self.angle + lon)
            for t in range(0, 361, 10):
                t_rad = math.radians(t)
                x = center_x + self.pulse_radius * math.sin(t_rad) * math.cos(angle)
                y = center_y + self.pulse_radius * math.sin(t_rad) * math.sin(angle)
                self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#00ffff", outline="")
        self.canvas.create_oval(
            center_x - 30, center_y - 30,
            center_x + 30, center_y + 30,
            fill="#00ffff", outline=""
        )
        self.angle = (self.angle + 8) % 360

    # --- Draw 3D Sphere animation (your animate logic) ---
    # (Copy the code from your animate() method here, but REMOVE the canvas.delete("all") line!)
    # ...existing code from self.animate(), starting after canvas.delete("all")...

    # Update rotation angles
        self.rotation_angle_y += self.rotation_speed_y
        self.rotation_angle_x += self.rotation_speed_x

    # Draw horizontal slices (parallels of latitude)
        for i in range(self.num_slices):
            phi = math.pi * (i / (self.num_slices - 1)) # 0 to pi radians
            y_sphere_coord = self.sphere_radius * math.cos(phi)
            effective_radius = self.sphere_radius * math.sin(phi)
            pA_x, pA_y, pA_z = self.rotate_point_3d(effective_radius, y_sphere_coord, 0, self.rotation_angle_x, self.rotation_angle_y)
            pB_x, pB_y, pB_z = self.rotate_point_3d(-effective_radius, y_sphere_coord, 0, self.rotation_angle_x, self.rotation_angle_y)
            pC_x, pC_y, pC_z = self.rotate_point_3d(0, y_sphere_coord, effective_radius, self.rotation_angle_x, self.rotation_angle_y)
            pD_x, pD_y, pD_z = self.rotate_point_3d(0, y_sphere_coord, -effective_radius, self.rotation_angle_x, self.rotation_angle_y)
            proj_pA_x, proj_pA_y = self.project_3d_to_2d(pA_x, pA_y, pA_z)
            proj_pB_x, proj_pB_y = self.project_3d_to_2d(pB_x, pB_y, pB_z)
            proj_pC_x, proj_pC_y = self.project_3d_to_2d(pC_x, pC_y, pC_z)
            proj_pD_x, proj_pD_y = self.project_3d_to_2d(pD_x, pD_y, pD_z)
            min_proj_x = min(proj_pA_x, proj_pB_x, proj_pC_x, proj_pD_x)
            max_proj_x = max(proj_pA_x, proj_pB_x, proj_pC_x, proj_pD_x)
            min_proj_y = min(proj_pA_y, proj_pB_y, proj_pC_y, proj_pD_y)
            max_proj_y = max(proj_pA_y, proj_pB_y, proj_pC_y, proj_pD_y)
            avg_z = (pA_z + pB_z + pC_z + pD_z) / 4
            if self.focal_length + avg_z < 10:
                continue
            hue = (i / self.num_slices) * 360
            color = self.get_color_from_depth(avg_z, self.sphere_radius, hue)
            self.canvas.create_oval(self.center_x + min_proj_x, self.center_y + min_proj_y,
                                    self.center_x + max_proj_x, self.center_y + max_proj_y,
                                    outline=color, width=1)
        for i in range(self.num_meridians):
            theta = (2 * math.pi / self.num_meridians) * i
            points = []
            zs = []
            for j in range(self.num_slices):
                phi = math.pi * (j / (self.num_slices - 1))
                x_3d = self.sphere_radius * math.sin(phi) * math.cos(theta)
                y_3d = self.sphere_radius * math.cos(phi)
                z_3d = self.sphere_radius * math.sin(phi) * math.sin(theta)
                rot_x, rot_y, rot_z = self.rotate_point_3d(x_3d, y_3d, z_3d, self.rotation_angle_x, self.rotation_angle_y)
                proj_x, proj_y = self.project_3d_to_2d(rot_x, rot_y, rot_z)
                points.append((self.center_x + proj_x, self.center_y + proj_y))
                zs.append(rot_z)
            if len(zs) > 0:
                avg_z_meridian = sum(zs) / len(zs)
            else:
                avg_z_meridian = 0
            if self.focal_length + avg_z_meridian < 10:
                continue
            hue = (theta / (2 * math.pi)) * 360 + 180
            color = self.get_color_from_depth(avg_z_meridian, self.sphere_radius, hue)
            self.canvas.create_line(points, smooth=True, fill=color, width=1)

    # Schedule next frame
        self.root.after(self.animation_speed, self.animate_combined)

    # def animate(self):
    #     self.center_x = self.canvas.winfo_width() / 2
    #     self.center_y = self.canvas.winfo_height() / 2
        # self.canvas.delete("all")  # Clear canvas for redraw

        # # Update rotation angles
        # self.rotation_angle_y += self.rotation_speed_y
        # self.rotation_angle_x += self.rotation_speed_x

        # # Draw horizontal slices (parallels of latitude)
        # for i in range(self.num_slices):
        #     phi = math.pi * (i / (self.num_slices - 1)) # 0 to pi radians

        #     y_sphere_coord = self.sphere_radius * math.cos(phi)
        #     effective_radius = self.sphere_radius * math.sin(phi)
        #     pA_x, pA_y, pA_z = self.rotate_point_3d(effective_radius, y_sphere_coord, 0, self.rotation_angle_x, self.rotation_angle_y)
        #     pB_x, pB_y, pB_z = self.rotate_point_3d(-effective_radius, y_sphere_coord, 0, self.rotation_angle_x, self.rotation_angle_y)
        #     pC_x, pC_y, pC_z = self.rotate_point_3d(0, y_sphere_coord, effective_radius, self.rotation_angle_x, self.rotation_angle_y)
        #     pD_x, pD_y, pD_z = self.rotate_point_3d(0, y_sphere_coord, -effective_radius, self.rotation_angle_x, self.rotation_angle_y)

        #     # Project these points to 2D
        #     proj_pA_x, proj_pA_y = self.project_3d_to_2d(pA_x, pA_y, pA_z)
        #     proj_pB_x, proj_pB_y = self.project_3d_to_2d(pB_x, pB_y, pB_z)
        #     proj_pC_x, proj_pC_y = self.project_3d_to_2d(pC_x, pC_y, pC_z)
        #     proj_pD_x, proj_pD_y = self.project_3d_to_2d(pD_x, pD_y, pD_z)

        #     # Determine bounding box for the ellipse
        #     min_proj_x = min(proj_pA_x, proj_pB_x, proj_pC_x, proj_pD_x)
        #     max_proj_x = max(proj_pA_x, proj_pB_x, proj_pC_x, proj_pD_x)
        #     min_proj_y = min(proj_pA_y, proj_pB_y, proj_pC_y, proj_pD_y)
        #     max_proj_y = max(proj_pA_y, proj_pB_y, proj_pC_y, proj_pD_y)

        #     # Calculate average depth for color. Use the average of all four points' z-coordinates
        #     avg_z = (pA_z + pB_z + pC_z + pD_z) / 4

        #     # Don't draw if it's completely behind the viewer (simple culling)
        #     # This uses the same logic as the perspective projection, so if focal_length + z < 0, it's behind.
        #     # We also make sure the ellipse is not "inverted" due to extreme rotation.
        #     if self.focal_length + avg_z < 10: # A small positive threshold
        #          continue

        #     hue = (i / self.num_slices) * 360
        #     color = self.get_color_from_depth(avg_z, self.sphere_radius, hue)

        #     self.canvas.create_oval(self.center_x + min_proj_x, self.center_y + min_proj_y,
        #                             self.center_x + max_proj_x, self.center_y + max_proj_y,
        #                             outline=color, width=1)

        # # Draw vertical lines (meridians)
        # for i in range(self.num_meridians):
        #     theta = (2 * math.pi / self.num_meridians) * i # Angle around the equator

        #     points = []
        #     zs = [] # Collect z-coordinates for depth calculation
        #     for j in range(self.num_slices): # Use num_slices points to define the arc
        #         phi = math.pi * (j / (self.num_slices - 1))

        #         # Spherical coordinates
        #         x_3d = self.sphere_radius * math.sin(phi) * math.cos(theta)
        #         y_3d = self.sphere_radius * math.cos(phi)
        #         z_3d = self.sphere_radius * math.sin(phi) * math.sin(theta)

        #         # Rotate and project
        #         rot_x, rot_y, rot_z = self.rotate_point_3d(x_3d, y_3d, z_3d, self.rotation_angle_x, self.rotation_angle_y)
        #         proj_x, proj_y = self.project_3d_to_2d(rot_x, rot_y, rot_z)

        #         points.append((self.center_x + proj_x, self.center_y + proj_y))
        #         zs.append(rot_z) # Store the rotated Z for depth coloring

        #     # Calculate average depth for color/visibility
        #     if len(zs) > 0:
        #         avg_z_meridian = sum(zs) / len(zs)
        #     else:
        #         avg_z_meridian = 0

        #     if self.focal_length + avg_z_meridian < 10: # Skip drawing if too far back or inverted
        #         continue

        #     hue = (theta / (2 * math.pi)) * 360 + 180 # Vary hue for meridians
        #     color = self.get_color_from_depth(avg_z_meridian, self.sphere_radius, hue)
        #     self.canvas.create_line(points, smooth=True, fill=color, width=1)

        # self.root.after(self.animation_speed, self.animate)

#     def animate_jarvis(self):
#         """Draw a large 3D pulsating, glowing sphere animation covering ~50% of the screen."""
#         self.canvas.delete("all")

#         canvas_width = self.master.winfo_width()
#         canvas_height = self.master.winfo_height()

#         # If window hasn't rendered yet, use initial dimensions
#         if canvas_width == 1: # Default value when window not yet rendered
#             canvas_width = self.WINDOW_WIDTH
#             canvas_height = self.WINDOW_HEIGHT

#         center_x, center_y = canvas_width // 2, canvas_height // 2

#         max_radius = min(canvas_width, canvas_height) * self.PULSE_MAX_RADIUS_FACTOR
#         min_radius = max_radius * self.PULSE_MIN_RADIUS_FACTOR

#         self.pulse_radius += self.pulse_direction * self.PULSE_SPEED
#         if self.pulse_radius > max_radius or self.pulse_radius < min_radius:
#             self.pulse_direction *= -1

#         # Draw concentric circles for 3D glow effect
#         for i in range(10, 0, -1):
#             r = self.pulse_radius * (i / 10)
#             self.canvas.create_oval(
#                 center_x - r, center_y - r,
#                 center_x + r, center_y + r,
#                 outline="#00FFFF", width=2 if i == 10 else 1
#             )

#         # Draw latitude lines to simulate a sphere
#         for lat in range(-60, 80, 30):
#             r_lat = self.pulse_radius * math.cos(math.radians(lat))
#             self.canvas.create_oval(
#                 center_x - r_lat, center_y - r_lat * math.sin(math.radians(lat)),
#                 center_x + r_lat, center_y + r_lat * math.sin(math.radians(lat)),
#                 outline="#00FFFF", width=1
#             )

#         # Draw longitude lines (as scattered dots for glow effect)
#         for lon in range(0, 180, 30):
#             angle = math.radians(self.angle + lon)
#             for t in range(0, 361, 10):
#                 t_rad = math.radians(t)
#                 x = center_x + self.pulse_radius * math.sin(t_rad) * math.cos(angle)
#                 y = center_y + self.pulse_radius * math.sin(t_rad) * math.sin(angle)
#                 self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#00ffff", outline="")

#         # Draw center glow
#         self.canvas.create_oval(
#             center_x - 30, center_y - 30,
#             center_x + 30, center_y + 30,
#             fill="#00ffff", outline=""
#         )

#         self.angle = (self.angle + 8) % 360
#         self.master.after(self.ANIMATION_DELAY_MS, self.animate_jarvis)


    def create_ui(self):
        """Create the user interface components."""
        chat_frame = tk.Frame(self.master, bg="blue")  # Removed bd and relief here
        chat_frame.place(relx=0.5, rely=0.9, anchor="s", width=1200, height=150)

        self.chat_window = scrolledtext.ScrolledText(
            chat_frame,
            bg="blue",
            wrap=tk.WORD,
            font=("Arial", 12),
            borderwidth=5,  # Increased border width for a more noticeable effect
            relief=tk.RAISED,  # Raised border
            highlightthickness=5,  # This will create the rounded corner effect
            highlightbackground="lightblue", # Color of the border
            highlightcolor="lightblue" # Color when focused
        )
        self.chat_window.pack(expand=True, fill="both", pady=(5, 0)) # Added some padding

        # Input field for user queries
        self.input_field = tk.Entry(
            chat_frame,
            bg="lightgray",
            font=("Arial", 12),
            borderwidth=3,  # Border width for the input field
            relief=tk.GROOVE,  # Groove relief for a sunken effect, which can enhance rounded corners
            highlightthickness=5,  # This will make the corners very rounded
            highlightbackground="darkgray", # Color of the border when not focused
            highlightcolor="blue" # Color of the border when focused
        )
        self.input_field.pack(side="left", padx=10, pady=5, expand=True, fill="x")

        # Frame for chat window and input field (positioned at bottom center)
#
        # Send button for manual input
        send_button = tk.Button(chat_frame, text="Send", command=self.send_manual_message, font=("Arial", 12))
        send_button.pack(side="right", padx=10, pady=5)


        # Language selection
        self.language_var = tk.StringVar(value="English")  # Default to English
        language_option_menu = tk.OptionMenu(self.master, self.language_var, *self.languages.keys())
        language_option_menu.config(font=("Arial", 14), bg="black", fg="white")
        language_option_menu.place(x=1200, y=50)

        # Filename input and buttons
        self.filename_area = tk.Text(self.master, bg="yellow", width=30, height=1, font=("Arial", 14))
        # self.filename_area.place(x=250, y=100)
        self.filename_area.insert(tk.END, "voice_notes.txt") # Default filename

    def send_manual_message(self):
        """Sends the text from the input field to the chatbot and processes it."""
        user_input = self.input_field.get().strip()
        if user_input:
            self.chat_window.insert(tk.END, f"You (Manual): {user_input}\n")
            self.input_field.delete(0, tk.END)
            # Process the command as if it came from voice
            self.process_command(user_input.lower())
            # Also get response from generative AI if it's not a direct command
            if not self.is_direct_command(user_input.lower()):
                response_text = self.get_response_from_gemini(user_input)
                self.chat_window.insert(tk.END, f"Bot: {response_text}\n\n")
                self.text_to_speech(response_text)

    def get_filename(self):
        """Get the filename from the user or use a default."""
        filename = self.filename_area.get("1.0", tk.END).strip()
        return filename if filename else "voice_notes.txt"

    def get_response_from_gemini(self, user_input):
        """Get a response from the Google Generative AI model."""
        try:
            response = self.chat_session.send_message(user_input)
            response_text = response.text
            return response_text
        except Exception as e:
            print(f"Error getting response from Gemini: {e}")
            return "Sorry, I couldn't connect to the AI model."

    def text_to_speech(self, text):
        """Convert text to speech."""
        try:
            selected_language = self.language_var.get()
            voices = self.engine.getProperty('voices')
            voice_found = False
            if selected_language == "Hindi":
                for voice in voices:
                    if "hindi" in voice.name.lower() or "hi" in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        voice_found = True
                        break
            else: # Default to English
                for voice in voices:
                    if "english" in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        voice_found = True
                        break
            if not voice_found:
                print(f"Warning: {selected_language} voice not found, using default.")

            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in text_to_speech: {e}")

    def take_voice(self, language, filename="voice_notes.txt"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        self.text_to_speech("Hey Aditya, I'm Rose. How can I help you?")

        while True:
            if not self.listening:
                self.text_to_speech("Listening paused. Say 'start listening' to resume.")
                while not self.listening:
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        try:
                            audio = recognizer.listen(source, timeout=self.LISTENING_TIMEOUT, phrase_time_limit=self.PHRASE_TIME_LIMIT)
                            command = recognizer.recognize_google(audio, language=language).lower()
                            if "start listening" in command:
                                self.listening = True
                                self.text_to_speech("Listening resumed.")
                                break
                        except sr.UnknownValueError:
                            # Silently ignore if nothing is recognized when paused
                            pass
                        except sr.WaitTimeoutError:
                            # Silently ignore timeout when paused
                            pass
                        except Exception as e:
                            print(f"Error during paused listening: {e}")
                continue

            try:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.text_to_speech("I'm Listening ")
                    audio = recognizer.listen(source, timeout=self.LISTENING_TIMEOUT, phrase_time_limit=self.PHRASE_TIME_LIMIT)
                    command = recognizer.recognize_google(audio, language=language).lower()
                    print(f"You said: {command}")
                    self.text_to_speech(f"You said: {command}")

                    voice_input = command.strip().lower()
                    self.chat_window.insert(tk.END, f"You (Voice): {voice_input}\n")
                    self.input_field.delete(0, tk.END)
                    self.input_field.insert(0, voice_input)

                    self.process_command(command)
                    save_content = voice_input
                    # timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    with open(filename, "a", encoding='utf-8') as file:
                        file.write( save_content + "\n")
                    self.chat_window.insert(tk.END, f"Saved to {filename}.\n\n")
                    if "start listening" in command:
                        self.listening = True
                        self.text_to_speech("Listening started.")
                        continue
                    if "stop listening" in command:
                        self.listening = False
                        self.text_to_speech("Listening stopped.")
                        continue

                    if command == "exit":
                        self.text_to_speech("Goodbye! See you next time.")
                        self.master.quit() # Graceful shutdown
                        break # Exit the listening loop

                    # If command was not a direct action, send to Gemini
                    if not self.is_direct_command(command):
                        response_text = self.get_response_from_gemini(command)
                        self.chat_window.insert(tk.END, f"Bot: {response_text}\n\n")
                        self.text_to_speech(response_text)

            except sr.UnknownValueError:
                self.text_to_speech("Sorry, I didn't catch that. Can you please repeat?")
            except sr.RequestError as e:
                self.text_to_speech(f"Could not request results from speech recognition service; {e}")
            except sr.WaitTimeoutError:
                self.text_to_speech("Listening timed out. Say 'start listening' to activate me.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.text_to_speech("An unexpected error occurred.")

    def set_filename(self, filename):
        """Set the filename in the filename_area from voice command."""
        filename = filename.strip()
        if not filename.lower().endswith(".txt"):
            filename += ".txt"
        self.filename_area.delete("1.0", tk.END)
        self.filename_area.insert(tk.END, filename)
        return filename if filename else "voice_notes.txt"


    def view_notes(self):
        """View saved notes."""
        filename = self.get_filename()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                content = file.read()
                self.chat_window.insert(tk.END, f"Notes in {filename}:\n{content}\n\n")
                self.text_to_speech(f"Displaying notes from {filename}.")
        else:
            self.chat_window.insert(tk.END, f"File '{filename}' not found.\n\n")
            self.text_to_speech("File not found.")
        return

    def delete_notes(self):
        """Delete saved notes."""
        filename = self.get_filename()
        if os.path.exists(filename):
            os.remove(filename)
            self.chat_window.insert(tk.END, f"Notes in '{filename}' deleted successfully.\n\n")
            self.text_to_speech("Notes deleted successfully.")
        else:
            self.chat_window.insert(tk.END, f"File '{filename}' not found.\n\n")
            self.text_to_speech("File not found.")
        return

    def save_text_to_file(self):
        """Save text from the input field to a file."""
        text = self.filename_area.get("1.0", tk.END).strip()
        if text:
            filename = self.get_filename()
            with open(filename, "a", encoding="utf-8") as file:
                file.write(text + "\n")
            self.chat_window.insert(tk.END, f"Text saved to {filename}.\n\n")
            self.text_to_speech(f"Text saved to {filename}.")
        else:
            self.chat_window.insert(tk.END, "No text to save.\n\n")
            self.text_to_speech("No text to save.")
        return

    def is_direct_command(self, command):
        """Helper to check if a command is a direct system/app command."""
        # This function helps decide whether to send to Gemini or execute a direct command
        # It needs to mirror the logic in process_command.
        app_commands = self._get_app_commands()
        close_commands = self._get_close_commands()
        system_commands = self._get_system_commands()
        assistant_commands = self._get_assistant_commands()  # <-- FIXED

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
            # "give filename": (self.get_filename(command), "Filename is retrieved"),
            "view notes": (self.view_notes, "Notes is opened"),
            "delete notes": (self.delete_notes, "Notes is deleted"),
            "save file": (self.save_text_to_file, "Text is saved to file"),
            "clear chat": (lambda: self.chat_window.delete(1.0, tk.END), "Chat cleared"),
        }

    def process_command(self, command):
        """Process voice commands."""

        app_commands = self._get_app_commands()
        close_commands = self._get_close_commands()
        system_commands = self._get_system_commands()
        assistant_commands = self._get_assistant_commands()  # <-- FIXED

        for keyword in ["open", "start", "launch", "run", "execute", "play", "use", "access", "go to", "browse", "visit", "search", "find", "show", "display", "activate"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in app_commands:
                    action, response = app_commands[app_name]
                    if callable(action): # For commands like "voice access" that use pyautogui
                        action()
                    else:
                        os.system(action)
                    self.text_to_speech(response)
                    return

        for keyword in ["close", "exit", "quit", "stop", "terminate", "end"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in close_commands:
                    action, response = close_commands[app_name]
                    os.system(action)
                    self.text_to_speech(response)
                    return

        if command in assistant_commands:
            action, response = assistant_commands[command]
            action()
            self.text_to_speech(response)
            return

        if command.startswith("play ") and command.endswith(" on youtube"):
            song_query = command[len("play "):-len(" on youtube")].strip()
            if song_query:
                query = song_query.replace(" ", "+")
                search_url = f"https://www.youtube.com/results?search_query={query}" # Correct Youtube URL
                try:
                    response = requests.get(search_url)
                    video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                    if video_ids:
                        video_url = f"https://www.youtube.com/watch?v={video_ids[0]}" # Correct YouTube video URL
                        self.text_to_speech(f"Playing {song_query} on YouTube.")
                        self.listening = False  # Stop listening during video playback

                        # Use yt-dlp to get video duration
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
                            time.sleep(duration + 5) # Add a few seconds buffer
                        else:
                            time.sleep(180) # Default 3 minutes if duration not found

                        self.listening = True
                        self.text_to_speech("Song finished. I'm listening again.")
                    else:
                        self.text_to_speech("Sorry, I couldn't find that song on YouTube.")
                except Exception as e:
                    print(f"Error playing YouTube video: {e}")
                    self.text_to_speech("Sorry, I encountered an issue playing that on YouTube.")
            else:
                self.text_to_speech("Please tell me what song to play on YouTube.")
            return
        if command.startswith("give file name "):  # <-- Use this consistently
            file = command[len("give file name "):].strip()
            if file:
                self.set_filename(file)
                self.text_to_speech(f"Filename set to: {file}")
            else:
                self.text_to_speech("Please provide a filename.")
            return

        if command.startswith("search ") and command.endswith(" on google"):
            search_query = command[len("search "):-len(" on google")].strip()
            if search_query:
                query = search_query.replace(" ", "+")
                url = f"https://www.google.com/search?q={query}"
                webbrowser.open(url)
                self.text_to_speech(f"Searching for {search_query} on Google.")
            else:
                self.text_to_speech("Please tell me what to search for on Google.")
            return

        if command in system_commands:
            action, response = system_commands[command]
            os.system(action)
            self.text_to_speech(response)
            return

        # If no specific command matches, let Gemini handle it (this logic is handled in take_voice)
        # self.text_to_speech("I didn't understand that command. Can I help you with something else?")


    def voice_listening(self):
        """Start listening for voice commands in a separate thread."""
        language = self.languages[self.language_var.get()]
        threading.Thread(
            target=self.take_voice,
            args=(language,), # Pass only language
            daemon=True
        ).start()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = _test(root)
    root.mainloop()