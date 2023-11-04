import requests
import json
from ...core.config import settings

# Define the URL of the OpenAI API for transcriptions
TRANSCRIPTION_URL = 'https://api.openai.com/v1/audio/transcriptions'

# Define the URL of the MP4 file to transcribe
AUDIO_FILE_URL = 'http://funk-02dd.akamaized.net/22679/files/21/03/05/2951778/4-LFQpzh6PdWbGCnJf7mDK.mp4'

# Your OpenAI API key
OPENAI_API_KEY = settings.openai_key

def transcribe_audio(audio_url, model='whisper-1', language=None, prompt=None, response_format='srt', temperature=0):
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    # We retrieve the audio file content from the URL
    audio_file_content = requests.get(audio_url).content
    
    # Define the files for the multipart/form-data upload
    files = {
        'file': ('audio.mp4', audio_file_content, 'audio/mp4'),
        'model': (None, model),
        'language': (None, language),
        'prompt': (None, prompt),
        'response_format': (None, response_format),
        'temperature': (None, temperature)
    }

    # Make the POST request with the multipart/form-data
    response = requests.post(
        TRANSCRIPTION_URL,
        headers=headers,
        files=files
    )

    
    # Check the response status and return the JSON if successful.
    if response.ok:
        return response
    else:
        # If the request failed, print the status code and response content for debugging.
        print(f'Failed to transcribe audio: {response.status_code}')
        print(response.content)
        return None

# Call the function and print the result
result = transcribe_audio(AUDIO_FILE_URL)
if result:
    #print contents, its not json its srt
    print(result.content)
