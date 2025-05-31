import tkinter as tk
import os
import pyttsx3
import pyautogui
import speech_recognition as sr
from tkinter import scrolledtext
import speech_recognition as sr
import threading
from operator import ge
import google.generativeai as genai


class VirtualAssistant:
    """A simple voice assistant GUI application."""
    def __init__(self, master):
        self.master = master
        self.master.title("Virtual Assistant")
        self.master.geometry("500x1000")
        self.master.configure(bg="black")
        # self.master.resizable(False, False)

        self.languages = {"English": "en-US", "Hindi": "hi-IN"}
        self.listening = True  # Add this line

        # UI Components
        self.create_ui()
        self.voice_listening()

    def create_ui(self):
        """Create the user interface components."""
        tk.Label(
            self.master, text="Select Language:", bg="black", font=("Arial", 20), fg="white"
        ).pack(pady=10)

        self.language_var = tk.StringVar(value="English")
        tk.OptionMenu(
            self.master, self.language_var, *self.languages.keys()
        ).pack(pady=10)

        tk.Label(
            self.master, text="Enter Filename:", bg="black", font=("Arial", 16), fg="white"
        ).pack(pady=10)

        self.filename_area = tk.Text(self.master, width=20, height=1, font=("Arial", 16))
        self.filename_area.pack(pady=10)

        tk.Button(
            self.master, text="Save Text to File", command=self.save_text_to_file
        ).pack(pady=10)

        listen_btn = tk.Canvas(self.master, width=80, height=80, highlightthickness=0, bg="black")
        listen_btn.pack(pady=10)
        circle = listen_btn.create_oval(10, 10, 70, 70, fill="#2196F3", outline="#2196F3")
        listen_btn.create_text(40, 40, text="🎤", fill="white", font=("Arial", 28, "bold"))

        def on_listen_click(event):
            self.start_listening()

        listen_btn.tag_bind(circle, "<Button-1>", on_listen_click)
        listen_btn.tag_bind("all", "<Button-1>", on_listen_click)

        self.chat_window = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=50, height=15)
        self.chat_window.pack(padx=10, pady=10)

    # Input field for user queries
        self.input_field = tk.Entry(self.master, width=40)
        self.input_field.pack(side=tk.LEFT, padx=(10, 5))

        tk.Button(
            self.master, text="View Notes", command=self.view_notes
        ).pack(pady=10)

        tk.Button(
            self.master, text="Delete Notes", command=self.delete_notes
        ).pack(pady=10)

        tk.Button(self.master, text="Quit", command=self.quit).pack(pady=10)

    def get_filename(self):
        """Get the filename from the user or use a default."""
        filename = self.filename_area.get("1.0", tk.END).strip()
        return filename if filename else "voice_notes.txt"

    def save_text_to_file(self):
        """Save text to a file."""
        text = self.filename_area.get("1.0", tk.END).strip()
        if text:
            filename = self.get_filename()
            with open(filename, "a", encoding="utf-8") as file:
                file.write(text + "\n")
            print(f"Text saved to {filename}")
        else:
            print("No text to save.")

    def get_language_choice(self):
    # Get the language code from the user
        languages={
            "1": "en-US",
            "2": "hi-IN",
        # Add more languages as needed
        }
        self.text_to_speech("Available languages:")
        self.text_to_speech("1. English (US)")
        # playsound(r"C:\Users\nanua\OneDrive\Desktop\PROJECT\py\hindi k.mp3")
        
    # Add more languages as needed
        choice = input("Select a language (1-2):")
        return languages.get(choice)  


    def view_notes(self):
        """View saved notes."""
        filename = self.get_filename()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                print(file.read())
        else:
            print("File not found.")

    def delete_notes(self):
        """Delete saved notes."""
        filename = self.get_filename()
        if os.path.exists(filename):
            os.remove(filename)
            print("Notes deleted successfully.")
        else:
            print("File not found.")

    def quit(self):
        """Quit the application."""
        self.master.quit()
    

# Function to generate chatbot response
    def get_response1(self, chat_window, input_field):
        import google.generativeai as genai
        API_KEY = "AIzaSyBla75QrCuFRBHQSXEjrfJUSLEcVY7TlA4"
        genai.configure(api_key=API_KEY)

        model = genai.GenerativeModel("gemini-2.0-flash")
        chat = model.start_chat()

        user_input = input_field.get()
        if not user_input.strip():
            return "No input provided."

        response = chat.send_message(user_input)

        # Display user query and chatbot response in the chat window
        chat_window.insert(tk.END, f"You: {user_input}\n")
        chat_window.insert(tk.END, f"Bot: {response.text}\n\n")

        # Clear the input field
        input_field.delete(0, tk.END)
        return response.text
    

    def text_to_speech(self, text):
        """Convert text to speech."""
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Set speech rate
            engine.setProperty('volume', 1)  # Set volume level (0.0 to 1.0)
            selected_language = self.language_var.get()
            voices = engine.getProperty('voices')
            if selected_language == "Hindi":
            # Try to find a Hindi voice
                for voice in voices:
                    if "hindi" in voice.name.lower() or "hi" in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
                else:
                    print("Hindi voice not found, using default.")
            else:
            # Use the first English voice found
                for voice in voices:
                    if "english" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("")

    def take_voice(self, language, chat_window, input_field):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        self.text_to_speech("Hey Aditya, I'm Rose.")

        while True:
            if not self.listening:
                self.text_to_speech("Listening paused. Say 'start listening' to resume.")
                # Wait for "start listening" command
                while not self.listening:
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        try:
                            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                            command = recognizer.recognize_google(audio, language=language).lower()
                            if "start listening" in command:
                                self.listening = True
                                self.text_to_speech("Listening resumed.")
                                break
                        except Exception:
                            pass
                continue

            try:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.text_to_speech("I'm Listening ")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio, language=language).lower()
                    print(f"You said: {command}")
                    self.text_to_speech(f"You said: {command}")

                    # Always update chat window and input field with recognized command
                    voice_input = command.strip().lower()
                    chat_window.insert(tk.END, f"Recognized Voice Input: {voice_input}\n")
                    input_field.delete(0, tk.END)
                    input_field.insert(0, voice_input)

                    # Always call process_command
                    self.process_command(command)

                    if "start listening" in command:
                        self.listening = True
                        self.text_to_speech("Listening started.")
                        continue
                    if "stop listening" in command:
                        self.listening = False
                        self.text_to_speech("Listening stopped.")
                        continue

                    if command == "exit":
                        self.text_to_speech("Goodbye! see you next time.")
                        self.master.quit()
                        os._exit(0)

            except sr.UnknownValueError:
                self.text_to_speech("")
            except sr.RequestError as e:
                self.text_to_speech("")
            except Exception as e:
                self.text_to_speech("")

    def process_command(self, command):
        """Process voice commands."""
        app_commands = {
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
        "Apache NetBeans": ("start netbeans", "Opening Apache NetBeans."),
        "next track": ("nircmd mediaplay next", "Skipping to the next track."),
        "previous track": ("nircmd mediaplay prev", "Going back to the previous track."),
        "play music": ("start wmplayer", "Opening Windows Media Player."),
        "pause music": ("nircmd mediaplay pause", "Pausing music playback."),
        }
        close_commands = {
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
        "gmail": ("taskkill /f /im chrome.exe", "Closing Gmail."),
        "youtube": ("taskkill /f /im chrome.exe", "Closing YouTube."),
        "google": ("taskkill /f /im chrome.exe", "Closing Google."),
        "facebook": ("taskkill /f /im chrome.exe", "Closing Facebook."),
        "twitter": ("taskkill /f /im chrome.exe", "Closing Twitter."),
        "whatsapp": ("taskkill /f /im chrome.exe", "Closing WhatsApp."),
        "instagram": ("taskkill /f /im chrome.exe", "Closing Instagram."),
        "linkedin": ("taskkill /f /im chrome.exe", "Closing LinkedIn."),
        "stack overflow": ("taskkill /f /im chrome.exe", "Closing Stack Overflow."),
        "github": ("taskkill /f /im chrome.exe", "Closing GitHub."),
        "reddit": ("taskkill /f /im chrome.exe", "Closing Reddit."),
        "quora": ("taskkill /f /im chrome.exe", "Closing Quora."),
        "amazon": ("taskkill /f /im chrome.exe", "Closing Amazon."),
        "flipkart": ("taskkill /f /im chrome.exe", "Closing Flipkart."),
        "news": ("taskkill /f /im chrome.exe", "Closing News."),
        "weather": ("taskkill /f /im chrome.exe", "Closing Weather."),
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
        "Apache NetBeans": ("taskkill /f /im netbeans64.exe", "Closing Apache NetBeans."),
        "voice access": (lambda: pyautogui.hotkey("win", "h"), "Opening voice access mode."),
        "music": ("nircmd mediaplay stop", "Stopping music playback."),
        
        }
        commands = {
        "restart the system": ("shutdown /r /t 5", "Restarting the system."),
        "shutdown the system": ("shutdown /s /t 5", "Shutting down the system."),
        "lock the system": ("rundll32.exe user32.dll,LockWorkStation", "Locking the system."),
        "sleep the system": ("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", "Putting the system to sleep."),
        "hibernate the system": ("rundll32.exe powrprof.dll,SetSuspendState 1,1,0", "Hibernating the system."),
        "log off": ("shutdown /l", "Logging off the current user."),
    }

        for keyword in ["open", "start", "launch","run", "execute","play", "use", "access","go to", "browse", "visit","search","find", "show", "display","activate"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in app_commands:
                    action, response = app_commands[app_name]
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

        if command in commands:
            action, response = commands[command]
            if callable(action):
                action()
            else:
                os.system(action)
            self.text_to_speech(response)
        elif command == "exit":
            self.text_to_speech("Goodbye!")
            self.quit()
        else:
            self.text_to_speech("")

    def voice_listening(self):
        """Start listening for voice commands."""
        language = self.languages[self.language_var.get()]
        threading.Thread(
                target=self.take_voice,
                args=(language, self.chat_window, self.input_field),
                daemon=True
            ).start()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualAssistant(root)
    root.mainloop()