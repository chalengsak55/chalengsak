"""
Whisper Transcription Module
Handles audio transcription using OpenAI's Whisper API
"""

import os
import openai
from typing import Optional, Dict, Any
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhisperTranscriber:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Whisper transcriber
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
    
    def transcribe_audio(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper API
        
        Args:
            audio_file_path: Path to the audio file
            language: Language code (default: "en" for English)
            
        Returns:
            Dictionary containing transcription results and metadata
        """
        try:
            logger.info(f"Starting transcription for file: {audio_file_path}")
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            # Open and transcribe the audio file
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",  # Get detailed response with timestamps
                    temperature=0.0  # More deterministic results
                )
            
            # Extract the transcription text and metadata
            result = {
                "text": transcript.text.strip(),
                "language": transcript.language,
                "duration": getattr(transcript, 'duration', None),
                "segments": getattr(transcript, 'segments', []),
                "success": True,
                "error": None
            }
            
            logger.info(f"Transcription successful. Text length: {len(result['text'])} characters")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                "text": "",
                "language": None,
                "duration": None,
                "segments": [],
                "success": False,
                "error": str(e)
            }
    
    def transcribe_audio_blob(self, audio_blob: bytes, filename: str = "audio.webm", language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio from bytes (for uploaded files)
        
        Args:
            audio_blob: Audio data as bytes
            filename: Original filename (for format detection)
            language: Language code (default: "en" for English)
            
        Returns:
            Dictionary containing transcription results and metadata
        """
        try:
            logger.info(f"Starting transcription for audio blob, filename: {filename}")
            
            # Create a temporary file to store the audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(audio_blob)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe the temporary file
                result = self.transcribe_audio(temp_file_path, language)
                return result
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Blob transcription failed: {str(e)}")
            return {
                "text": "",
                "language": None,
                "duration": None,
                "segments": [],
                "success": False,
                "error": str(e)
            }
    
    def is_transcription_valid(self, transcription_result: Dict[str, Any], min_length: int = 10) -> bool:
        """
        Check if transcription result is valid and meaningful
        
        Args:
            transcription_result: Result from transcribe_audio method
            min_length: Minimum character length for valid transcription
            
        Returns:
            True if transcription is valid, False otherwise
        """
        if not transcription_result.get("success", False):
            return False
        
        text = transcription_result.get("text", "").strip()
        
        # Check minimum length
        if len(text) < min_length:
            logger.warning(f"Transcription too short: {len(text)} characters (minimum: {min_length})")
            return False
        
        # Check for common transcription failures
        failure_indicators = [
            "thank you for watching",
            "thanks for watching", 
            "please subscribe",
            "[Music]",
            "[Applause]",
            "..."
        ]
        
        text_lower = text.lower()
        for indicator in failure_indicators:
            if indicator in text_lower and len(text) < 50:
                logger.warning(f"Detected potential transcription failure: '{indicator}' in short text")
                return False
        
        return True

def test_transcription():
    """
    Test function for the transcription module
    """
    try:
        transcriber = WhisperTranscriber()
        
        # Test with a sample audio file (if available)
        test_file = "test_audio.wav"
        if os.path.exists(test_file):
            result = transcriber.transcribe_audio(test_file)
            print("Transcription Result:")
            print(f"Success: {result['success']}")
            print(f"Text: {result['text']}")
            print(f"Language: {result['language']}")
            print(f"Valid: {transcriber.is_transcription_valid(result)}")
        else:
            print("No test audio file found. Transcriber initialized successfully.")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_transcription()