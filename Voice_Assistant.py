import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import speech_recognition as sr
import threading
import os
import pyautogui
from PIL import Image, ImageTk # Keep if you plan to use images later

# --- Configuration ---
# IMPORTANT: Replace "YOUR_API_KEY_HERE" with your actual Google Gemini API key.
# It is highly recommended to load API keys from environment variables for security.
# Example: API_KEY = os.getenv("GOOGLE_API_KEY")
# API_KEY =  # Placeholder - REPLACE THIS!
genai.configure(api_key=API_KEY)

# --- Global Variables for persistent objects ---
engine = None # pyttsx3 engine
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat() # For persistent conversation history

def text_to_speech(text):
    """Converts text to speech using pyttsx3 in a separate thread."""
    def speak():
        global engine
        if engine is None:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
            except Exception as e:
                print(f"Error initializing text-to-speech engine: {e}")
                return
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error during text-to-speech: {e}")
    threading.Thread(target=speak, daemon=True).start()

def get_response(user_input):
    """Sends user input to the Gemini model and displays the response."""
    if not user_input.strip():
        chat_window.insert(tk.END, "Bot: No input provided.\n\n")
        text_to_speech("No input provided.")
        return

    try:
        response = chat.send_message(user_input)
        response_text = response.text
    except Exception as e:
        response_text = f"An error occurred while getting response: {e}"
        print(response_text)

    chat_window.insert(tk.END, f"You: {user_input}\n")
    chat_window.insert(tk.END, f"Bot: {response_text}\n\n")
    chat_window.yview(tk.END) # Auto-scroll to the bottom
    text_to_speech(response_text)
    input_field.delete(0, tk.END)

def process_command(command):
    """Processes voice commands to open/close applications or perform system actions."""
    app_commands = {
        "notepad": ("notepad.exe", "Opening Notepad."),
        "calculator": ("calc.exe", "Opening Calculator."),
        "file explorer": ("explorer.exe", "Opening File Explorer."),
        "command prompt": ("cmd.exe", "Opening Command Prompt."),
        "task manager": ("taskmgr.exe", "Opening Task Manager."),
        "gmail": ("start chrome https://mail.google.com", "Opening Gmail."),
        "youtube": ("start chrome https://www.youtube.com", "Opening YouTube."), # Fixed URL
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
    }
    close_commands = {
        "notepad": ("taskkill /f /im notepad.exe", "Closing Notepad."),
        "calculator": ("taskkill /f /im calc.exe", "Closing Calculator."),
        "file explorer": ("taskkill /f /im explorer.exe", "Closing File Explorer."),
        "command prompt": ("taskkill /f /im cmd.exe", "Closing Command Prompt."),
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
        "apache netbeans": ("taskkill /f /im netbeans64.exe", "Closing Apache NetBeans."),
    }
    system_commands = { # Renamed from 'commands' to avoid confusion with command parameter
        "restart the system": ("shutdown /r /t 5", "Restarting the system."),
        "shutdown the system": ("shutdown /s /t 5", "Shutting down the system."),
        "open voice access": (lambda: pyautogui.hotkey("win", "h"), "Opening voice access mode."),
    }

    # Handle open/start/launch commands
    for keyword in ["open", "start", "launch"]:
        if command.startswith(keyword):
            app_name = command[len(keyword):].strip()
            if app_name in app_commands:
                action, response = app_commands[app_name]
                os.system(action)
                text_to_speech(response)
                return

    # Handle close commands
    if command.startswith("close"):
        app_name = command[len("close"):].strip()
        if app_name in close_commands:
            action, response = close_commands[app_name]
            os.system(action)
            text_to_speech(response)
            return

    # Handle general system commands
    if command in system_commands:
        action, response = system_commands[command]
        if callable(action):
            action()
        else:
            os.system(action)
        text_to_speech(response)
        return

    # If no specific command is matched, treat as a general query for the AI
    get_response(command)


def voice_to_input():
    """Continuously listens for voice input and processes it."""
    recognizer = sr.Recognizer()
    text_to_speech("Hello, Aditya. I am Rose, your assistant.")
    while True:
        with sr.Microphone() as source:
            try:
                chat_window.insert(tk.END, "Listening to your command.\n")
                chat_window.yview(tk.END)
                text_to_speech("Listening to your command.")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                voice_input = recognizer.recognize_google(audio)
                chat_window.insert(tk.END, f"Recognized Voice Input: {voice_input}\n")
                chat_window.yview(tk.END)
                text_to_speech(f"You said: {voice_input}")
                input_field.delete(0, tk.END)
                input_field.insert(0, voice_input)

                lower_voice_input = voice_input.lower()

                if lower_voice_input == "search":
                    text_to_speech("What do you want to search?")
                    chat_window.insert(tk.END, "What do you want to search?\n")
                    chat_window.yview(tk.END)
                    while True: # Inner loop for search mode
                        with sr.Microphone() as source2:
                            recognizer.adjust_for_ambient_noise(source2, duration=0.5)
                            audio2 = recognizer.listen(source2, timeout=10, phrase_time_limit=10)
                            try:
                                question = recognizer.recognize_google(audio2)
                                chat_window.insert(tk.END, f"Searching for: {question}\n")
                                chat_window.yview(tk.END)
                                input_field.delete(0, tk.END)
                                input_field.insert(0, question)

                                if question.lower() == "exit from search":
                                    text_to_speech("Exiting search mode.")
                                    chat_window.insert(tk.END, "Exiting search mode.\n\n")
                                    chat_window.yview(tk.END)
                                    break # Exit inner search loop
                                if question.lower() == "clear":
                                    chat_window.insert(tk.END, "Clearing chat...\n")
                                    chat_window.delete(1.0, tk.END)
                                    continue # Continue inner search loop, don't process as general query
                                if question.lower() == "exit":
                                    chat_window.insert(tk.END, "Exiting the application...\n")
                                    chat_window.yview(tk.END)
                                    app.quit()
                                    return # Exit main loop and function
                                get_response(question) # Send the question to Gemini

                            except sr.UnknownValueError:
                                chat_window.insert(tk.END, "Could not understand audio in search mode.\n")
                                chat_window.yview(tk.END)
                            except sr.RequestError as e:
                                chat_window.insert(tk.END, f"Could not request results from Google Speech Recognition service; {e}\n")
                                chat_window.yview(tk.END)
                            except Exception as e:
                                chat_window.insert(tk.END, f"An error occurred during search input: {e}\n")
                                chat_window.yview(tk.END)
                                break # Exit search loop on other errors

                elif lower_voice_input == "clear":
                    chat_window.insert(tk.END, "Clearing chat...\n")
                    chat_window.delete(1.0, tk.END)
                    chat_window.yview(tk.END)
                    continue
                elif lower_voice_input == "exit":
                    chat_window.insert(tk.END, "Exiting the application...\n")
                    chat_window.yview(tk.END)
                    app.quit()
                    break
                else:
                    text_to_speech("Processing your command.")
                    process_command(lower_voice_input)

            except sr.UnknownValueError:
                chat_window.insert(tk.END, "Could not understand audio.\n")
                chat_window.yview(tk.END)
            except sr.RequestError as e:
                chat_window.insert(tk.END, f"Could not request results from Google Speech Recognition service; {e}\n")
                chat_window.yview(tk.END)
            except Exception as e:
                chat_window.insert(tk.END, f"An error occurred during voice input: {e}\n")
                chat_window.yview(tk.END)

def start_listening():
    """Starts the voice recognition thread."""
    threading.Thread(target=voice_to_input, daemon=True).start()

# --- GUI Setup ---
app = tk.Tk()
app.title("Rose Assistant")
app.geometry("800x800")
app.configure(bg="black", padx=10, pady=10)



chat_window = scrolledtext.ScrolledText(app, wrap=tk.WORD, bg="lightgreen", fg="black", width=100, height=30, font=("Arial", 12))
chat_window.place(x=20, y=20)
chat_window.insert(tk.END, "Say something you want or type it\n")
chat_window.insert(tk.END, "Say 'clear' to clear the chat\n")
chat_window.insert(tk.END, "Say 'exit' to close the application\n\n")


input_field = tk.Entry(app, width=50)
input_field.place(x=20, y=600)

# Bind Enter key to send message from input_field
def send_message_from_entry(event=None):
    user_input = input_field.get()
    if user_input:
        get_response(user_input)
    else:
        chat_window.insert(tk.END, "You: (empty input)\n")
        chat_window.yview(tk.END)

input_field.bind("<Return>", send_message_from_entry)

# Add a send button for text input
send_button = tk.Button(app, text="Send", command=send_message_from_entry)
send_button.place(x=450, y=600)


start_listening()

app.mainloop()