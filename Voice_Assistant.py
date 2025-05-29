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
    commands = {
        "open notepad": ("notepad.exe", "Opening Notepad."),
        "start notepad": ("notepad.exe", "Opening Notepad."),
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
        "close instagram": ("taskkill /f /im chrome.exe", "Closing Instagram."),
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
        "restart the system": ("shutdown /r /t 5", "Restarting the system."),
        "shutdown the system": ("shutdown /s /t 5", "Shutting down the system."),
        "open voice access": (lambda: pyautogui.hotkey("win", "h"), "Opening voice access mode."),
    }

    if command in commands:
        action, response = commands[command]
        if callable(action):
            action()
        else:
            text_to_speech(response)
            os.system(action)
    else:
        text_to_speech("Command not recognized.")

def voice_to_input():
    recognizer = sr.Recognizer()
    text_to_speech("Hello, Aditya. I am Rose, your personal assistant.")
    while True:
        with sr.Microphone() as source:
            try:
                chat_window.insert(tk.END, "Listening to your command.\n")
                text_to_speech("Listening to your command.")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
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
                        
                            except sr.UnknownValueError:
                                chat_window.insert(tk.END, "Sorry, I could not understand the search query. Please try again.\n")
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
            except sr.UnknownValueError:
                chat_window.insert(tk.END, "Sorry, I could not understand the audio.\n")
            except sr.RequestError as e:
                chat_window.insert(tk.END, f"Could not request results; {e}\n")
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