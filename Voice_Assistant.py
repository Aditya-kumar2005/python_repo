import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import speech_recognition as sr
import threading
import os
import pyautogui

API_KEY = "AIzaSyBla75QrCuFRBHQSXEjrfJUSLEcVY7TlA4"
genai.configure(api_key=API_KEY)

def text_to_speech(text):
    def speak():
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.setProperty('rate', 150)
            engine.runAndWait()
        except Exception as e:
            print(f"An error occurred in text-to-speech: {e}")
    threading.Thread(target=speak, daemon=True).start()

def get_response(user_input):
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat()

    if not user_input.strip():
        return "No input provided."

    response = chat.send_message(user_input)

    chat_window.insert(tk.END, f"You: {user_input}\n")
    chat_window.insert(tk.END, f"Bot: {response.text}\n\n")
    text_to_speech(response.text)
    input_field.delete(0, tk.END)
    return response.text

def process_command(command):
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
        "Apache NetBeans": ("taskkill /f /im netbeans64.exe", "Closing Apache NetBeans."),
        }
        commands = {
        "restart the system": ("shutdown /r /t 5", "Restarting the system."),
        "shutdown the system": ("shutdown /s /t 5", "Shutting down the system."),
        "open voice access": (lambda: pyautogui.hotkey("win", "h"), "Opening voice access mode."),
    }

        for keyword in ["open", "start", "launch"]:
            if command.startswith(keyword):
                app_name = command[len(keyword):].strip()
                if app_name in app_commands:
                    action, response = app_commands[app_name]
                    os.system(action)
                    text_to_speech(response)
                    return

    # Handle close
        if command.startswith("close"):
           app_name = command[len("close"):].strip()
           if app_name in close_commands:
               action, response = close_commands[app_name]
               os.system(action)
               text_to_speech(response)
               return

        if command in commands:
            action, response = commands[command]
            if callable(action):
                action()
            else:
                os.system(action)
            text_to_speech(response)
def voice_to_input():
    recognizer = sr.Recognizer()
    text_to_speech("Hello, Aditya. I am Rose, your personal assistant.")
    while True:
        with sr.Microphone() as source:
            try:
                chat_window.insert(tk.END, "Listening to your command.\n")
                text_to_speech("Listening to your command.")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
                voice_input = recognizer.recognize_google(audio)
                chat_window.insert(tk.END, f"Recognized Voice Input: {voice_input}\n")
                text_to_speech(f"You said: {voice_input}")
                input_field.delete(0, tk.END)
                input_field.insert(0, voice_input)
                if voice_input.lower() == "search":
                    text_to_speech("What do you want to search?")
                    chat_window.insert(tk.END, "What do you want to search?\n")
                    while True:
                        with sr.Microphone() as source2:
                            recognizer.adjust_for_ambient_noise(source2, duration=0.5)
                            audio2 = recognizer.listen(source2, timeout=5, phrase_time_limit=10)
                            try:
                                question = recognizer.recognize_google(audio2)
                                chat_window.insert(tk.END, f"Searching for: {question}\n")
                                input_field.delete(0, tk.END)
                                input_field.insert(0, question)
                                get_response(question)
                                if question.lower() == "exit from search":                                 
                                    text_to_speech("Exiting search mode.")
                                    break
                        
                            except Exception as e:
                                chat_window.insert(tk.END, f"An error occurred: {e}\n")
                                break
                        
                    continue

                else:
                    text_to_speech("Processing your command.")
                    process_command(voice_input.lower())
                if voice_input.lower() == "clear":
                    chat_window.insert(tk.END, "clearing chat...\n")
                    chat_window.delete(1.0, tk.END)
                    continue
                if voice_input.lower() == "exit":
                    chat_window.insert(tk.END, "Exiting the application...\n")
                    app.quit()
                    break
            except Exception as e:
                chat_window.insert(tk.END, f"An error occurred: {e}\n")

def start_listening():
    threading.Thread(target=voice_to_input, daemon=True).start()

# Create the main application window
app = tk.Tk()
app.title("Virtual Assistant")
app.geometry("600x800")
app.configure(bg="black")

chat_window = scrolledtext.ScrolledText(app, wrap=tk.WORD, bg="green", fg="white", width=100, height=30, font=("Arial", 12))
chat_window.insert(tk.END, "Welcome to the Generative AI Chatbot!\n")
chat_window.insert(tk.END, "Say something you want or type it\n")
chat_window.insert(tk.END, "Say 'clear' to clear the chat\n")
chat_window.insert(tk.END, "Say 'exit' to close the application\n")
chat_window.pack(padx=10, pady=10)

input_field = tk.Entry(app, width=50)
input_field.pack(padx=10, pady=10)

start_listening()

app.mainloop()