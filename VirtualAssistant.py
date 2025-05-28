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

        # UI Components
        self.create_ui()
        self.start_listening()

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


    # Voice input button
        # self.voice_button = tk.Button(self.master, text="Voice Input", command=lambda: threading.Thread(target=self.take_voice, args=(self.languages[self.language_var.get()],), daemon=True).start())
        # self.voice_button.pack(side=tk.LEFT, padx=(5, 10))


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
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"An error occurred in text-to-speech: {e}")

    def take_voice(self, language, chat_window, input_field):
        """Continuously capture voice input and process commands."""
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        self.text_to_speech("Hey Aditya, I'm Rose.")

        while True:
            try:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.text_to_speech("I'm Listening ")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio, language=language).lower()
                    print(f"You said: {command}")
                    self.text_to_speech(f"You said: {command}")
                
                    # Process the command
                    if command == "exit":
                        self.text_to_speech("Goodbye! see you next time.")
                        self.master.quit()
                        os._exit(0)
                        
                    self.process_command(command)

                    if command.strip() == "{command} search in chatbot":
                        self.text_to_speech("Searching in chatbot.")
                        self.get_response1(self.chat_window, self.input_field)
                        continue
                    voice_input = command.strip().lower()
                    self.chat_window.insert(tk.END, f"Recognized Voice Input: {voice_input}\n")

                     # Write the recognized text into the input field
                    self.input_field.delete(0, tk.END)  # Clear the input field
                    self.input_field.insert(0, voice_input) 
            except sr.UnknownValueError:
                self.text_to_speech("Sorry, I couldn't understand that. Please try again.")
            except sr.RequestError:
                self.text_to_speech("There was an issue with the speech recognition service.")
            except sr.WaitTimeoutError:
                self.text_to_speech("Listening timed out. Please try again.")
            except Exception as e:
                self.text_to_speech(f"An error occurred: {e}")

    def process_command(self, command):
        """Process voice commands."""
        commands = {
            "open notepad" or "start notepad": ("notepad.exe", "Opening Notepad."),
            "open calculator": ("calc.exe", "Opening Calculator."),
            "open file explorer": ("explorer.exe", "Opening File Explorer."),
            "open command prompt": ("cmd.exe", "Opening Command Prompt."),
            "open task manager": ("taskmgr.exe", "Opening Task Manager."),
            "open gmail": ("start chrome https://mail.google.com", "Opening Gmail."),
            "open youtube": ("start chrome https://www.youtube.com", "Opening YouTube."),
            "open google": ("start chrome https://www.google.com", "Opening Google."),
            "open facebook": ("start chrome https://www.facebook.com", "Opening Facebook."),
            "open twitter": ("start chrome https://www.twitter.com", "Opening Twitter."),
            "open whatsapp": ("start chrome https://web.whatsapp.com", "Opening WhatsApp."),
            "open instagram": ("start chrome https://www.instagram.com", "Opening Instagram."),
            "open linkedin": ("start chrome https://www.linkedin.com", "Opening LinkedIn."),
            "open stack overflow": ("start chrome https://stackoverflow.com", "Opening Stack Overflow."),
            "open github": ("start chrome https://github.com", "Opening GitHub."),
            "open reddit": ("start chrome https://www.reddit.com", "Opening Reddit."),
            "open quora": ("start chrome https://www.quora.com", "Opening Quora."),
            "open amazon": ("start chrome https://www.amazon.com", "Opening Amazon."),
            "open flipkart": ("start chrome https://www.flipkart.com", "Opening Flipkart."),
            "open news": ("start chrome https://news.google.com", "Opening News."),
            "open weather": ("start chrome https://weather.com", "Opening Weather."),
            "open calendar": ("start outlookcal:", "Opening Calendar."),
            "open clock": ("start ms-clock:", "Opening Clock."),
            "open settings": ("start ms-settings:", "Opening Settings."),
            "open control panel": ("control", "Opening Control Panel."),
            "open task scheduler": ("taskschd.msc", "Opening Task Scheduler."),
            "open snipping tool": ("snippingtool", "Opening Snipping Tool."),
            "open paint": ("mspaint", "Opening Paint."),
            "open word": ("start winword", "Opening Microsoft Word."),
            "open excel": ("start excel", "Opening Microsoft Excel."),
            "open powerpoint": ("start powerpnt", "Opening Microsoft PowerPoint."),
            "open access": ("start msaccess", "Opening Microsoft Access."),
            "open publisher": ("start mspub", "Opening Microsoft Publisher."),
            "open onenote": ("start onenote", "Opening Microsoft OneNote."),
            "open teams": ("start teams", "Opening Microsoft Teams."),
            "open skype": ("start skype", "Opening Skype."),
            "open zoom": ("start zoom", "Opening Zoom."),
            "open discord": ("start discord", "Opening Discord."),
            "open slack": ("start slack", "Opening Slack."),
            "open notepad++": ("start notepad++.exe", "Opening Notepad++."),
            "open sublime text": ("start sublime_text.exe", "Opening Sublime Text."),
            "open visual studio": ("start devenv", "Opening Visual Studio."),
            "open eclipse": ("start eclipse", "Opening Eclipse."),
            "open pycharm": ("start pycharm", "Opening PyCharm."),
            "open intellij": ("start idea", "Opening IntelliJ IDEA."),
            "open android studio": ("start studio64", "Opening Android Studio."),
            "open Apache NetBeans": ("start netbeans", "Opening Apache NetBeans."),
            #add more applications as needed
            "close notepad": ("taskkill /f /im notepad.exe", "Closing Notepad."),
            "close calculator": ("taskkill /f /im calc.exe", "Closing Calculator."),
            "close file explorer": ("taskkill /f /im explorer.exe", "Closing File Explorer."),
            "close command prompt": ("taskkill /f /im cmd.exe", "Closing Command Prompt."),
            "close task manager": ("taskkill /f /im taskmgr.exe", "Closing Task Manager."),
            "close gmail": ("taskkill /f /im chrome.exe", "Closing Gmail."),
            "close youtube": ("taskkill /f /im chrome.exe", "Closing YouTube."),
            "close google": ("taskkill /f /im chrome.exe", "Closing Google."),
            "close facebook": ("taskkill /f /im chrome.exe", "Closing Facebook."),
            "close twitter": ("taskkill /f /im chrome.exe", "Closing Twitter."),
            "close whatsapp": ("taskkill /f /im chrome.exe", "Closing WhatsApp."),
            "close instagram": ("taskkill /f /im chrome.exe" , "Closing Instagram."),
            "close linkedin": ("taskkill /f /im chrome.exe", "Closing LinkedIn."),
            "close stack overflow": ("taskkill /f /im chrome.exe", "Closing Stack Overflow."),
            "close github": ("taskkill /f /im chrome.exe", "Closing GitHub."),
            "close reddit": ("taskkill /f /im chrome.exe", "Closing Reddit."),
            "close quora": ("taskkill /f /im chrome.exe", "Closing Quora."),
            "close amazon": ("taskkill /f /im chrome.exe", "Closing Amazon."),
            "close flipkart": ("taskkill /f /im chrome.exe", "Closing Flipkart."),
            "close news": ("taskkill /f /im chrome.exe", "Closing News."),
            "close weather": ("taskkill /f /im chrome.exe", "Closing Weather."),
            "close calendar": ("taskkill /f /im outlook.exe", "Closing Calendar."),
            "close clock": ("taskkill /f /im Time.exe", "Closing Clock."),
            "close settings": ("taskkill /f /im SystemSettings.exe", "Closing Settings."),
            "close control panel": ("taskkill /f /im control.exe", "Closing Control Panel."),
            "close task scheduler": ("taskkill /f /im mmc.exe", "Closing Task Scheduler."),
            "close snipping tool": ("taskkill /f /im SnippingTool.exe", "Closing Snipping Tool."),
            "close paint": ("taskkill /f /im mspaint.exe", "Closing Paint."),
            "close word": ("taskkill /f /im WINWORD.EXE", "Closing Microsoft Word."),
            "close excel": ("taskkill /f /im EXCEL.EXE", "Closing Microsoft Excel."),
            "close powerpoint": ("taskkill /f /im POWERPNT.EXE", "Closing Microsoft PowerPoint."),
            "close access": ("taskkill /f /im MSACCESS.EXE", "Closing Microsoft Access."),
            "close publisher": ("taskkill /f /im MSPUB.EXE", "Closing Microsoft Publisher."),
            "close onenote": ("taskkill /f /im ONENOTE.EXE", "Closing Microsoft OneNote."),
            "close teams": ("taskkill /f /im Teams.exe", "Closing Microsoft Teams."),
            "close skype": ("taskkill /f /im Skype.exe", "Closing Skype."),
            "close zoom": ("taskkill /f /im Zoom.exe", "Closing Zoom."),
            "close discord": ("taskkill /f /im Discord.exe", "Closing Discord."),
            "close slack": ("taskkill /f /im slack.exe", "Closing Slack."),
            "close notepad++": ("taskkill /f /im notepad++.exe", "Closing Notepad++."),
            "close sublime text": ("taskkill /f /im sublime_text.exe", "Closing Sublime Text."),
            "close visual studio": ("taskkill /f /im devenv.exe", "Closing Visual Studio."),
            "close eclipse": ("taskkill /f /im eclipse.exe", "Closing Eclipse."),
            "close pycharm": ("taskkill /f /im pycharm64.exe", "Closing PyCharm."),
            "close intellij": ("taskkill /f /im idea64.exe", "Closing IntelliJ IDEA."),
            "close android studio": ("taskkill /f /im studio64.exe", "Closing Android Studio."),
            "close Apache NetBeans": ("taskkill /f /im netbeans64.exe", "Closing Apache NetBeans."),
            # add more for closing applications as needed
            # some system commands
            "restart the system": ("shutdown /r /t 5", "Restarting the system."),
            "shutdown the system": ("shutdown /s /t 5", "Shutting down the system."),
            "open voice access": (lambda: pyautogui.hotkey("win", "h"), "Opening voice access mode."),
        }

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
        elif command == "open chatbot":
            if not self.is_chatbot_running():
                self.launch_chatbot()
            else:
                self.text_to_speech("Chatbot is already running.")
        elif command == "close chatbot":
            self.close_chatbot()
        elif command == "start voice input":
            self.start_voice_input()
        elif command == "send message":
            self.send_message()
        else:
            self.text_to_speech("Command not recognized.")

    def start_listening(self):
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