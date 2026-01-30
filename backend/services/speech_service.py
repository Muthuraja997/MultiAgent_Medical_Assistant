"""
Speech Service

Business logic for speech-to-text and text-to-speech operations.
"""

import os
import uuid
import sys
from pydub import AudioSegment
from elevenlabs.client import ElevenLabs
import requests

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from core.config import Config

# Load configuration
config = Config()

# Initialize ElevenLabs client
client = ElevenLabs(
    api_key=config.speech.eleven_labs_api_key,
)

# Speech directory (in common folder)
SPEECH_DIR = "../common/uploads/speech"
os.makedirs(SPEECH_DIR, exist_ok=True)


class SpeechService:
    """Service class for speech-related operations"""
    
    @staticmethod
    async def transcribe_audio(audio_content: bytes, filename: str) -> str:
        """
        Transcribe audio to text using ElevenLabs API.
        
        Args:
            audio_content: Audio file content in bytes
            filename: Original filename
            
        Returns:
            str: Transcribed text
        """
        try:
            # Save the audio file temporarily
            temp_audio = f"./{SPEECH_DIR}/speech_{uuid.uuid4()}.webm"
            
            with open(temp_audio, "wb") as f:
                f.write(audio_content)
            
            # Check file size
            file_size = os.path.getsize(temp_audio)
            print(f"Received audio file size: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError("Received empty audio file")
            
            # Convert to MP3
            mp3_path = f"./{SPEECH_DIR}/speech_{uuid.uuid4()}.mp3"
            
            try:
                # Use pydub with format detection
                audio = AudioSegment.from_file(temp_audio)
                audio.export(mp3_path, format="mp3")
                
                mp3_size = os.path.getsize(mp3_path)
                print(f"Converted MP3 file size: {mp3_size} bytes")

                with open(mp3_path, "rb") as mp3_file:
                    audio_data = mp3_file.read()
                print(f"Converted audio file into byte array successfully!")

                transcription = client.speech_to_text.convert(
                    file=audio_data,
                    model_id="scribe_v1",
                    tag_audio_events=True,
                    language_code="eng",
                    diarize=True,
                )
                
                # Clean up temp files
                try:
                    os.remove(temp_audio)
                    os.remove(mp3_path)
                    print(f"Deleted temp files: {temp_audio}, {mp3_path}")
                except Exception as e:
                    print(f"Could not delete file: {e}")
                
                if transcription.text:
                    return transcription.text
                else:
                    raise Exception(f"API error: {transcription}")

            except Exception as e:
                print(f"Error processing audio: {str(e)}")
                raise Exception(f"Error processing audio: {str(e)}")
                    
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise Exception(f"Transcription error: {str(e)}")
    
    @staticmethod
    def generate_speech(text: str, voice_id: str = "EXAMPLE_VOICE_ID") -> str:
        """
        Generate speech from text using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            
        Returns:
            str: Path to generated audio file
        """
        try:
            if not text:
                raise ValueError("Text is required")
            
            # Define API request to ElevenLabs
            elevenlabs_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": config.speech.eleven_labs_api_key
            }
            payload = {
                "text": text,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }

            # Send request to ElevenLabs API
            response = requests.post(elevenlabs_url, headers=headers, json=payload)

            if response.status_code != 200:
                raise Exception(
                    f"Failed to generate speech, status: {response.status_code}, "
                    f"details: {response.text}"
                )
            
            # Save the audio file temporarily
            temp_audio_path = f"./{SPEECH_DIR}/{uuid.uuid4()}.mp3"
            with open(temp_audio_path, "wb") as f:
                f.write(response.content)

            return temp_audio_path

        except Exception as e:
            raise Exception(f"Speech generation error: {str(e)}")
