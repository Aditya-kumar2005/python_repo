# This document provides an explanation of the Virtual Assistant and a step-by-step guide to setting up and running the application.

## Virtual Assistant
The Virtual Assistant is a voice-controlled desktop assistant application built using Python. It leverages several libraries to provide functionalities such as voice recognition, text-to-speech, opening and closing applications, performing web searches, playing YouTube videos, and interacting with a generative AI model.

Key Features:

1.Voice Control:                 Interact with the assistant using natural voice commands.
2.Text-to-Speech:                The assistant responds verbally to your commands and queries.
3.Application Management:        Open and close various desktop applications and system tools (e.g., Notepad, Calculator, Chrome, Task Manager).
4.Web Browse:                    Open popular websites like Google, YouTube, Facebook, and more.
5.Web Search:                    Perform Google searches directly through voice commands.
6.YouTube Integration:           Play specific songs or videos on YouTube.
7.System Commands:               Execute system-level actions like restarting, shutting down, locking, or sleeping the system.
8.Note-Taking:                   Save, view, and delete voice notes or typed text to a file.
9.Generative AI Integration:     Utilize Google's Gemini-2.0-flash model to get intelligent responses to general questions and queries.
10.Customizable Language:        Switch between English and Hindi for voice recognition and responses.
11.Pulsating Visualizer:         A dynamic, pulsating sphere animation provides visual feedback for the assistant's activity.
12.User-Friendly Interface:      A Tkinter-based GUI with a chat window for displaying interactions and an input field for manual commands.
13.Setup Guide:                  Running Your Virtual Assistant

## To run the Virtual Assistant, you need to set up your Python environment and install the necessary libraries. Follow these steps:

### Step 1:= Install Python
If you don't have Python installed, download and install the latest version from the official Python website: [https://www.python.org/downloads/]

Important: During installation, make sure to check the box that says "Add Python to PATH" or "Add python.exe to your PATH". This will make it easier to run Python commands from your command prompt.

### Step 2: Install Required Libraries
Open your command prompt or terminal and run the following command to install all the necessary Python libraries:

Bash:==`pip install pyttsx3 pyautogui SpeechRecognition google-generativeai requests yt-dlp Pillow numpy tk`    


pyttsx3:              For text-to-speech capabilities.
pyautogui:            For automating GUI interactions (e.g., hotkeys for voice access).
SpeechRecognition:    For converting spoken language to text.
google-generativeai:  To interact with Google's Generative AI models (Gemini).
requests:             For making HTTP requests (e.g., for Youtubees).
yt-dlp:               A command-line program to download videos from YouTube and other video sites (used here to get video duration).
Pillow(PIL):          For image processing, used by tkinter for displaying images.
numpy:                For numerical operations (though its usage might be minimal in the provided code, it's often a dependency for other libraries).
tk:                   Tkinter is usually included with Python installations, but tk might be needed on some systems.


### Step 3: Obtain a Google Generative AI API Key
The Virtual Assistant uses Google's Generative AI (Gemini) for intelligent conversations. You need an API key to access this service.

Go to the Google AI Studio: [https://aistudio.google.com/]
Sign in with your Google account.
Create a new API key if you don't have one already.
Copy your API key.

### Step 4: Configure the API Key in the VirtualAssistant.py file
Open the `VirtualAssistant.py file` in a text editor. Locate the following line:

   > GOOGLE_API_KEY = ?
**Replace ? with the actual API key you obtained from Google AI Studio.**

Security Best Practice (Optional but Recommended):
For production environments, it's highly recommended to store your API key as an environment variable instead of hardcoding it. You can set an environment variable named GOOGLE_API_KEY on your system and then modify the line in VirtualAssistant.py to:

    >GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
This keeps your API key out of your code.

### Step 5: Install nircmd (for advanced media and system control on Windows)

Some commands like "next track" or "pause music" utilize nircmd. This is a third-party command-line utility for Windows.

Download nircmd from the official NirSoft website: [https://www.nirsoft.net/utils/nircmd.html]
Extract the `nircmd.exe` file.
Place nircmd.exe in a directory that is included in your system's PATH environment variable (e.g., `C:\Windows` or `C:\Windows\System32`), or in the same directory as your  `VirtualAssistant.py` file.

### Step 6: Run the Virtual Assistant
Open your command prompt or terminal.

Navigate to the directory where you saved `VirtualAssistant.py`.
(e.g., cd path\to\your\virtual_assistant_folder)

Run the application using the Python interpreter:

Bash:=  `python VirtualAssistant.py`


A GUI window for the Virtual Assistant should appear. The assistant will greet you and start listening for commands.

Troubleshooting:=
 
"No module named..." error: This means you missed installing a library in Step 2. Double-check the pip install command and ensure all libraries are installed.
Microphone Issues:  Ensure your microphone is properly connected and configured in your operating system's sound settings.
Check if your antivirus or firewall is blocking the application from accessing the microphone.
Try speaking clearly and at a moderate pace.
API Key Errors: If you get errors related to the Generative AI model, double-check that your API key is correct and that you have an active internet connection.
nircmd not found: If media control commands don't work, ensure nircmd.exe is in a directory listed in your system's PATH, or in the same folder as VirtualAssistant.py.
"File not found" for notes: The assistant will create `voice_notes.txt` in the same directory as `VirtualAssistant.py` by default. Ensure your user account has write permissions to that directory.
