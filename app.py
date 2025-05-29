from operator import ge
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
    

def get_response(user_input):
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat()

    if not user_input.strip():
        return "No input provided."

    # Send the user input to the chatbot
    response = chat.send_message(user_input)

    # Display user query and chatbot response in the chat window
    chat_window.insert(tk.END, f"You: {user_input}\n")
    chat_window.insert(tk.END, f"Bot: {response.text}\n\n")

    text_to_speech(response.text)  # Convert response to speech

    # Return the chatbot's response
    input_field.delete(0, tk.END)
    return response.text



def text_to_speech(text):
    """Convert text to speech."""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.setProperty('rate', 150)  # Set speech rate
        engine.runAndWait()
    except Exception as e:
        print(f"An error occurred in text-to-speech: {e}")

# Function to capture voice input and write it into the input field
def voice_to_input():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    engine.say("Hello,Aditya I am Rose your personal assistant")
    engine.setProperty('rate', 150)  # Set speech rate
    engine.runAndWait()
    while True:
        with sr.Microphone() as source:
            try:
                # Adjust for ambient noise and listen for voice input
                          
                chat_window.insert(tk.END, "Listening to your command.\n")
                text_to_speech("Listening to your command.")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

                # Recognize speech using Google Web Speech API
                voice_input = recognizer.recognize_google(audio)
                chat_window.insert(tk.END, f"Recognized Voice Input: {voice_input}\n")
                text_to_speech(f"You said: {voice_input}")
                input_field.delete(0, tk.END)  # Clear the input field
                input_field.insert(0, voice_input)  # Insert recognized text into input field
                # Get response from the chatbot
                get_response(voice_input)

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

# Create the main application window
app = tk.Tk()
app.title("Generative AI Chatbot")
app.geometry("600x800")
app.configure(bg="black")

# Chat window to display messages
chat_window = scrolledtext.ScrolledText(app, wrap=tk.WORD, bg="green", fg="white", width=100, height=150, font=("Arial", 12))
chat_window.insert(tk.END, "Welcome to the Generative AI Chatbot!\n")

chat_window.insert(tk.END, "Say something you want or type it\n")

chat_window.insert(tk.END, "Say 'clear' to clear the chat\n")

chat_window.insert(tk.END, "Say 'exit' to close the application\n")

chat_window.pack(padx=10, pady=10)

# Input field for user queries
input_field = tk.Entry(app, width=50)
input_field.pack(padx=10, pady=10)

threading.Thread(target=voice_to_input, daemon=True).start()
# Start the Tkinter main event loop
app.mainloop()






