from operator import ge
import google.generativeai as genai
import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr

API_KEY = "AIzaSyBla75QrCuFRBHQSXEjrfJUSLEcVY7TlA4"
genai.configure(api_key=API_KEY)

# Function to generate chatbot response
def get_response1():
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

# Add these functions in app.py
def trigger_send_button():
    # Simulate clicking the "Send" button
    get_response1()

def trigger_voice_input_button():
    # Simulate clicking the "Voice Input" button
    voice_to_input()

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

    # Return the chatbot's response
    input_field.delete(0, tk.END)
    return response.text

# Function to capture voice input and write it into the input field
def voice_to_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            # Adjust for ambient noise and listen for voice input
            chat_window.insert(tk.END, "Listening for voice input...\n")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

            # Recognize speech using Google Web Speech API
            voice_input = recognizer.recognize_google(audio)
            chat_window.insert(tk.END, f"Recognized Voice Input: {voice_input}\n")

            # Write the recognized text into the input field
            input_field.delete(0, tk.END)  # Clear the input field
            input_field.insert(0, voice_input)  # Insert the recognized text
        except sr.UnknownValueError:
            chat_window.insert(tk.END, "Sorry, I could not understand the audio.\n")
        except sr.RequestError as e:
            chat_window.insert(tk.END, f"Could not request results; {e}\n")
        except Exception as e:
            chat_window.insert(tk.END, f"An error occurred: {e}\n")

# Create the main application window
app = tk.Tk()
app.title("Generative AI Chatbot")

# Chat window to display messages
chat_window = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=50, height=35)
chat_window.pack(padx=10, pady=10)

# Input field for user queries
input_field = tk.Entry(app, width=40)
input_field.pack(side=tk.LEFT, padx=(10, 5))

# Send button to submit queries
send_button = tk.Button(app, text="Send", command=get_response1)
send_button.pack(side=tk.LEFT, padx=(5, 10))

# Voice input button
voice_button = tk.Button(app, text="Voice Input", command=voice_to_input)
voice_button.pack(side=tk.LEFT, padx=(5, 10))

# Start the Tkinter main event loop
app.mainloop()






