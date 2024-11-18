#Voice Assistant App
This repository contains a voice-enabled assistant built using Python and Streamlit. The assistant leverages APIs like OpenAI, Google, and OpenWeather to perform tasks such as speech recognition, web searches, email reading, and more.

#Features

Speech-to-Text: Converts user voice inputs into text using OpenAI's Whisper API.
Text-to-Speech: Responds with audio playback using a text-to-speech model.
Email Management: Reads and summarizes the last few emails from your inbox.
Web Search: Performs online searches and summarizes the results.
Weather Updates: Fetches real-time weather information for any city.
Reminders: Adds and manages reminders locally.
Daily News Summary: Summarizes the latest news and sends it to your email.

#Requirements

Python 3.7 or higher
Streamlit
OpenAI Python SDK
Additional dependencies in requirements.txt


How to Run


#Clone this repository:

git clone https://github.com/your-username/voice-assistant.git
cd voice-assistant


#Install dependencies:

pip install -r requirements.txt


#Start the Streamlit app:

streamlit run app.py


#Open the app in your browser and interact with the assistant.

#API Keys Setup

OpenAI API Key
Google API Key (optional for search)
OpenWeather API Key

#Replace placeholders in the script with your API keys for full functionality.

#Note

Ensure sensitive information (e.g., email credentials and API keys) is handled securely and not shared publicly.
