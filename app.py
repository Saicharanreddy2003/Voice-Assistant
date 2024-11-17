import streamlit as st
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pydub import AudioSegment
import pygame
from openai import OpenAI
from openai import OpenAI
import imaplib
import email
from email.header import decode_header
import chardet  # You can install this package using: pip install chardet
import webbrowser
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

reminders = []
# Initialize OpenAI client
client = OpenAI(api_key="sk-proj-UhYBYmB9GV1YHpVrgoLGT3BlbkFJOMjwoJGc8U7Wml5P1LcP")

def ttt(system_content, user_content):
    import datetime
    system_content += "IMP: DONT GIVE MARKDOWN RESPONSES OR BULLET POINTS. JUST GIVE PLAIN TEXT RESPONSES. THE RESPONSES MUST BE FRIENDLY AND ENGAGING BUT DONT INCLUDE IMAGES."
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    system_content = f"{system_content} Today's date is {today_date} and the time is {time_now}. If the user asks for it, spell it out."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content

def stt(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"

    )
    return transcription.text

def tts(text):
    speech_file_path = "speech.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova",
        input=text,
    ) as response:
        response.stream_to_file(speech_file_path)
    return speech_file_path

def decision_maker(user_prompt):
    system_prompt = """ 
    You are an assistant that can help the user with various queries. You have a bunch of tools at your disposal. Please choose an appropriate tool for answering the user query.
    Tools:
    1. read_last_n_emails() - Reads the last n emails from the user's inbox.
    2. openbrowser_and_show() - Opens a browser and shows the user the search results for the query "tomatoes".
    3. get_weather(city) - Returns the weather information for the given city.
    4. add_todo() - Adds a reminder to the assistant.
    5. websearch(query) - Searches the web for the given query and returns the results.
    6. news_summary() - Generates a news summary and sends it to the user via email.
    7. None - if you don't require any tool to answer the user query.
    Your response must be like this in a json format.
    {
        "tool": "tool_name",
        "topic": "topic_name"
    }
        example:
    User: "Can you read my last 5 emails?"
    {
        "tool": "read_last_n_emails",
        "topic": 5
    }
    User: "Can you show me the weather in New York?"
    {
        "tool": "get_weather",
        "topic": "New York"
    }
    User: send me news summary
    {
        "tool": "news_summary",
        "topic": ""
    }
    User: "Can you show me the search results for 'Machine Learning'?"
    {
        "tool": "openbrowser_and_show",
        "topic": "Machine Learning"
    }
    User: "what is 1+1?"
    {
        "tool": "None",
        "topic": "2"
    }
    User: "what is the capital of India?" 
    {
        "tool": "None",
        "topic": "The capital of India is New Delhi" 
    }
    For None tool, the topic should be the answer to the user query and it must be really short and concise (max 3 -4 lines)
    """
    decision = ttt(system_prompt, user_prompt)
    decision = decision.replace("```", "").replace("json", "")
    decision = eval(decision)
    tool = decision["tool"]
    topic = decision["topic"]
    return tool, topic

def read_last_n_emails(n):
    # Connect to the Gmail IMAP server
    imap_server = "imap.gmail.com"
    user = "phanihrushik.35@gmail.com"
    password = "ayek lkip imwu jjpc"  # Use an app password if you have 2FA enabled

    # Create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)

    # Login to your account
    imap.login(user, password)

    # Select the mailbox you want to read (INBOX)
    imap.select("inbox")

    # Search for all emails
    status, messages = imap.search(None, "ALL")

    # Get a list of email IDs
    email_ids = messages[0].split()

    # Get the last n emails
    last_n_email_ids = email_ids[-n:]

    # Initialize email counter and result string
    email_counter = 1
    result = ""

    for email_id in last_n_email_ids:
        # Fetch the email by ID
        status, msg_data = imap.fetch(email_id, "(RFC822)")

        # Parse the email content
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # If it's a bytes object, decode it
                    subject = subject.decode(encoding if encoding else "utf-8")

                # Decode the email sender
                from_ = msg.get("From")

                # Add sender and subject to the result string
                result += f"{email_counter}. Email from: {from_}\n"
                result += f"   Subject: {subject}\n"

                # If the email message is multipart
                if msg.is_multipart():
                    for part in msg.walk():
                        # Extract the email body
                        if part.get_content_type() == "text/plain":
                            try:
                                # Try to decode with UTF-8 first
                                body = part.get_payload(decode=True).decode("utf-8")
                            except UnicodeDecodeError:
                                # If decoding fails, detect encoding using chardet
                                raw_data = part.get_payload(decode=True)
                                detected_encoding = chardet.detect(raw_data)['encoding']
                                body = raw_data.decode(detected_encoding)
                            # Add the body to the result string
                            result += f"   Body: {body}\n\n"
                else:
                    # If the message is not multipart, get the payload directly
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8")
                    except UnicodeDecodeError:
                        # If decoding fails, detect encoding using chardet
                        raw_data = msg.get_payload(decode=True)
                        detected_encoding = chardet.detect(raw_data)['encoding']
                        body = raw_data.decode(detected_encoding)
                    # Add the body to the result string
                    result += f"   Body: {body}\n\n"

        # Increment the email counter
        email_counter += 1

    # Close the connection and logout
    imap.close()
    imap.logout()

    # Return the result string
    return result

def openbrowser_and_show(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

def get_weather(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': "7a0b454edf726bbb65255a8f71f593c6",
        'units': 'metric'  # Use 'imperial' for Fahrenheit
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if response.status_code == 200:
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"Weather: {weather}, Temperature: {temperature}°C"
    else:
        return f"Error: {data['message']}"

def add_todo():
    reminder = input("What would you like to be reminded of? ")
    time = input("When should I remind you? ")
    reminders.append((reminder, time))
    print("Reminder added successfully!")

def websearch(query):

  import http.client
  import json

  conn = http.client.HTTPSConnection("google.serper.dev")
  payload = json.dumps({
    "q": query 
  })
  headers = {
    'X-API-KEY': 'b786226533843ebfb7937d4b177e19918e019653',
    'Content-Type': 'application/json'
  }
  conn.request("POST", "/search", payload, headers)
  res = conn.getresponse()
  data = res.read()

  # Parse the JSON data
  json_data = json.loads(data.decode("utf-8"))

  # Extract headlines and snippets
  webresults = ""
  for result in json_data["organic"]:
      headline = result["title"]
      snippet = result["snippet"]
      webresults += f"{headline}: {snippet}\n"
      
  res = ttt(f"You are a helful assistant summarising the web results for the query. User query : {query}", f"webresults: {webresults}")
  return res

def news_summary():
    """Generate news summary and send it to user via email"""
    tech_summary = websearch("latest technology news")
    business_summary = websearch("latest business news India")
    sports_summary = websearch("latest sports news India")
    health_summary = websearch("latest health news India")
    science_summary = websearch("latest science news India")

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
            }}
            .container {{
                width: 90%;
                max-width: 800px;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .section {{
                margin-bottom: 20px;
            }}
            h2 {{
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 4px;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
            }}
            .footer {{
                text-align: center;
                font-size: 14px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Daily News Summary</h1>

            <div class="section">
                <h2>Technology</h2>
                <p>{tech_summary}</p>
            </div>

            <div class="section">
                <h2>Business</h2>
                <p>{business_summary}</p>
            </div>

            <div class="section">
                <h2>Sports</h2>
                <p>{sports_summary}</p>
            </div>

            <div class="section">
                <h2>Health</h2>
                <p>{health_summary}</p>
            </div>

            <div class="section">
                <h2>Science</h2>
                <p>{science_summary}</p>
            </div>

            <div class="footer">
                <p>Have a nice day!</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Email setup
    email = "phanihrushik.35@gmail.com"
    receiver_email = "saicharanreddys2003@gmail.com"
    password = "ayek lkip imwu jjpc"  # Be cautious when handling sensitive information like passwords

    subject = "Today's News Summary :)"

    # Create a multipart message and set headers
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = receiver_email

    # Attach the HTML version of the message
    part = MIMEText(html_body, "html")
    msg.attach(part)

    # Send email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    server.sendmail(email, receiver_email, msg.as_string())
    server.quit()

    print("Email sent successfully!")

# Streamlit frontend
st.title("Voice Assistant")
st.write("Click the button below to start recording your query!")

# Record button
if st.button("Record"):
    duration = 4
    sample_rate = 44100

    # Record audio
    with st.spinner("Recording..."):
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype='int16')
        sd.wait()  # Wait for the recording to finish
        st.write("Recording finished!")

    # Save recorded audio
    wav_file = 'input_audio.wav'
    write(wav_file, sample_rate, audio_data)

    # Convert WAV to MP3
    audio = AudioSegment.from_wav(wav_file)
    audio.export('input_audio.mp3', format='mp3')

    # Transcribe the audio
    transcript = stt('input_audio.mp3')
    st.write(f"User said: {transcript}")

    # Decide action based on transcript
    tool, topic = decision_maker(transcript)


    if tool == "read_last_n_emails":
        result = read_last_n_emails(topic)
    
    elif tool == "openbrowser_and_show":
        openbrowser_and_show(topic)
        result = "Opening browser and showing search results"
    
    elif tool == "get_weather":
        result = get_weather(topic)
    
    elif tool == "add_todo":
        add_todo()
        result = "Reminder added successfully!"
    
    elif tool == "websearch":
        result = websearch(topic)
    
    elif tool == "news_summary":
        st.write("Creating summary...")
        news_summary()
        result = "News summary generated and sent to your email!"
        
    elif tool == "None":
        result = topic

    # Display result
    st.write(f"Assistant said: {result}")

    # Convert result to speech and play
    output_audio = tts(result)
    st.audio(output_audio, autoplay=True)
