"""
Main Scoring Logic Module
Orchestrates the complete argument evaluation pipeline:
1. Audio transcription
2. GPT-4 feedback generation
3. Avatar video creation (optional)
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from whisper_transcribe import WhisperTranscriber
from gpt_feedback import GPTFeedbackGenerator
from avatar_gen import HeyGenAvatarGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArgumentScorer:
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 heygen_api_key: Optional[str] = None,
                 heygen_avatar_id: Optional[str] = None,
                 enable_avatar: bool = True):
        """
        Initialize the argument scorer with all required components
        
        Args:
            openai_api_key: OpenAI API key for Whisper and GPT-4
            heygen_api_key: HeyGen API key for avatar generation (optional)
            heygen_avatar_id: HeyGen avatar ID (optional)
            enable_avatar: Whether to enable avatar video generation
        """
        self.enable_avatar = enable_avatar
        
        # Initialize transcriber
        try:
            self.transcriber = WhisperTranscriber(api_key=openai_api_key)
            logger.info("Whisper transcriber initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper transcriber: {e}")
            raise
        
        # Initialize feedback generator
        try:
            self.feedback_generator = GPTFeedbackGenerator(api_key=openai_api_key)
            logger.info("GPT feedback generator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GPT feedback generator: {e}")
            raise
        
        # Initialize avatar generator (optional)
        if self.enable_avatar:
            try:
                self.avatar_generator = HeyGenAvatarGenerator(
                    api_key=heygen_api_key,
                    avatar_id=heygen_avatar_id
                )
                if self.avatar_generator.is_enabled():
                    logger.info("HeyGen avatar generator initialized successfully")
                else:
                    logger.warning("HeyGen avatar generator is disabled (no API key)")
            except Exception as e:
                logger.warning(f"Failed to initialize HeyGen avatar generator: {e}")
                self.avatar_generator = None
        else:
            self.avatar_generator = None
            logger.info("Avatar generation disabled by configuration")
    
    def process_audio_file(self, audio_file_path: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an audio file through the complete pipeline
        
        Args:
            audio_file_path: Path to the audio file
            context: Optional context about the debate topic
            
        Returns:
            Dictionary containing complete results
        """
        logger.info(f"Starting audio file processing: {audio_file_path}")
        
        # Initialize result structure
        result = {
            "timestamp": datetime.now().isoformat(),
            "audio_file": audio_file_path,
            "context": context,
            "transcription": None,
            "feedback": None,
            "avatar_video": None,
            "success": False,
            "error": None,
            "processing_steps": []
        }
        
        try:
            # Step 1: Transcribe audio
            logger.info("Step 1: Transcribing audio...")
            result["processing_steps"].append("transcription_started")
            
            transcription_result = self.transcriber.transcribe_audio(audio_file_path)
            result["transcription"] = transcription_result
            
            if not transcription_result.get("success"):
                raise Exception(f"Transcription failed: {transcription_result.get('error')}")
            
            if not self.transcriber.is_transcription_valid(transcription_result):
                raise Exception("Transcription is too short or invalid")
            
            result["processing_steps"].append("transcription_completed")
            logger.info(f"Transcription successful: {len(transcription_result['text'])} characters")
            
            # Step 2: Generate feedback
            logger.info("Step 2: Generating GPT feedback...")
            result["processing_steps"].append("feedback_started")
            
            feedback_result = self.feedback_generator.generate_feedback(
                transcription_result["text"],
                context
            )
            result["feedback"] = feedback_result
            
            if not feedback_result.get("success"):
                logger.warning(f"Feedback generation failed: {feedback_result.get('error')}")
                # Continue with fallback feedback
            
            result["processing_steps"].append("feedback_completed")
            logger.info(f"Feedback generated: Score {feedback_result.get('score', 'N/A')}")
            
            # Step 3: Generate avatar video (optional)
            if self.avatar_generator and self.avatar_generator.is_enabled():
                logger.info("Step 3: Generating avatar video...")
                result["processing_steps"].append("avatar_started")
                
                avatar_result = self.avatar_generator.create_reaction_video(feedback_result)
                result["avatar_video"] = avatar_result
                
                if avatar_result.get("success"):
                    logger.info(f"Avatar video generation started: {avatar_result.get('video_id')}")
                else:
                    logger.warning(f"Avatar video generation failed: {avatar_result.get('error')}")
                
                result["processing_steps"].append("avatar_completed")
            else:
                logger.info("Step 3: Avatar generation skipped (disabled or not configured)")
                result["avatar_video"] = {
                    "success": False,
                    "status": "disabled",
                    "message": "Avatar generation is disabled"
                }
            
            # Mark as successful
            result["success"] = True
            result["processing_steps"].append("pipeline_completed")
            logger.info("Audio processing pipeline completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Audio processing failed: {error_msg}")
            result["error"] = error_msg
            result["processing_steps"].append(f"pipeline_failed: {error_msg}")
            return result
    
    def process_audio_blob(self, audio_blob: bytes, filename: str = "recording.webm", context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process audio data from bytes (for uploaded files)
        
        Args:
            audio_blob: Audio data as bytes
            filename: Original filename
            context: Optional context about the debate topic
            
        Returns:
            Dictionary containing complete results
        """
        logger.info(f"Starting audio blob processing: {filename}")
        
        # Initialize result structure
        result = {
            "timestamp": datetime.now().isoformat(),
            "audio_file": filename,
            "context": context,
            "transcription": None,
            "feedback": None,
            "avatar_video": None,
            "success": False,
            "error": None,
            "processing_steps": []
        }
        
        try:
            # Step 1: Transcribe audio blob
            logger.info("Step 1: Transcribing audio blob...")
            result["processing_steps"].append("transcription_started")
            
            transcription_result = self.transcriber.transcribe_audio_blob(audio_blob, filename)
            result["transcription"] = transcription_result
            
            if not transcription_result.get("success"):
                raise Exception(f"Transcription failed: {transcription_result.get('error')}")
            
            if not self.transcriber.is_transcription_valid(transcription_result):
                raise Exception("Transcription is too short or invalid")
            
            result["processing_steps"].append("transcription_completed")
            logger.info(f"Transcription successful: {len(transcription_result['text'])} characters")
            
            # Step 2: Generate feedback
            logger.info("Step 2: Generating GPT feedback...")
            result["processing_steps"].append("feedback_started")
            
            feedback_result = self.feedback_generator.generate_feedback(
                transcription_result["text"],
                context
            )
            result["feedback"] = feedback_result
            
            if not feedback_result.get("success"):
                logger.warning(f"Feedback generation failed: {feedback_result.get('error')}")
                # Continue with fallback feedback
            
            result["processing_steps"].append("feedback_completed")
            logger.info(f"Feedback generated: Score {feedback_result.get('score', 'N/A')}")
            
            # Step 3: Generate avatar video (optional)
            if self.avatar_generator and self.avatar_generator.is_enabled():
                logger.info("Step 3: Generating avatar video...")
                result["processing_steps"].append("avatar_started")
                
                avatar_result = self.avatar_generator.create_reaction_video(feedback_result)
                result["avatar_video"] = avatar_result
                
                if avatar_result.get("success"):
                    logger.info(f"Avatar video generation started: {avatar_result.get('video_id')}")
                else:
                    logger.warning(f"Avatar video generation failed: {avatar_result.get('error')}")
                
                result["processing_steps"].append("avatar_completed")
            else:
                logger.info("Step 3: Avatar generation skipped (disabled or not configured)")
                result["avatar_video"] = {
                    "success": False,
                    "status": "disabled",
                    "message": "Avatar generation is disabled"
                }
            
            # Mark as successful
            result["success"] = True
            result["processing_steps"].append("pipeline_completed")
            logger.info("Audio blob processing pipeline completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Audio blob processing failed: {error_msg}")
            result["error"] = error_msg
            result["processing_steps"].append(f"pipeline_failed: {error_msg}")
            return result
    
    def get_avatar_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of an avatar video generation job
        
        Args:
            video_id: The video ID to check
            
        Returns:
            Dictionary containing status information
        """
        if not self.avatar_generator or not self.avatar_generator.is_enabled():
            return {
                "success": False,
                "status": "disabled",
                "message": "Avatar generation is not enabled"
            }
        
        return self.avatar_generator.check_video_status(video_id)
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "assets") -> str:
        """
        Save processing results to a JSON file
        
        Args:
            results: Results dictionary from processing
            output_dir: Directory to save results
            
        Returns:
            Path to the saved file
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"argument_results_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Save results
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    def get_processing_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of processing results
        
        Args:
            results: Results dictionary from processing
            
        Returns:
            Summary dictionary
        """
        summary = {
            "success": results.get("success", False),
            "timestamp": results.get("timestamp"),
            "audio_file": results.get("audio_file"),
            "processing_steps": len(results.get("processing_steps", [])),
            "error": results.get("error")
        }
        
        # Transcription summary
        transcription = results.get("transcription", {})
        if transcription.get("success"):
            summary["transcription"] = {
                "text_length": len(transcription.get("text", "")),
                "language": transcription.get("language"),
                "duration": transcription.get("duration")
            }
        
        # Feedback summary
        feedback = results.get("feedback", {})
        if feedback.get("success"):
            summary["feedback"] = {
                "score": feedback.get("score"),
                "emojis": feedback.get("emojis"),
                "comment": feedback.get("comment")
            }
        
        # Avatar video summary
        avatar = results.get("avatar_video", {})
        if avatar:
            summary["avatar_video"] = {
                "enabled": avatar.get("success", False),
                "status": avatar.get("status"),
                "video_id": avatar.get("video_id")
            }
        
        return summary

def test_scoring_pipeline():
    """
    Test function for the complete scoring pipeline
    """
    try:
        # Initialize scorer
        scorer = ArgumentScorer(enable_avatar=False)  # Disable avatar for testing
        
        # Test with sample audio file (if available)
        test_file = "test_audio.wav"
        if os.path.exists(test_file):
            print("Testing with audio file...")
            results = scorer.process_audio_file(test_file, context="Testing the argument scoring system")
            
            print(f"Success: {results['success']}")
            if results['success']:
                summary = scorer.get_processing_summary(results)
                print("Summary:")
                print(json.dumps(summary, indent=2))
            else:
                print(f"Error: {results['error']}")
        else:
            print("No test audio file found. Scorer initialized successfully.")
            print("Available methods:")
            print("- process_audio_file()")
            print("- process_audio_blob()")
            print("- get_avatar_video_status()")
            print("- save_results()")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_scoring_pipeline()