"""
HeyGen Avatar Generation Module
Handles AI avatar video generation using HeyGen API
"""

import os
import requests
import json
import time
from typing import Optional, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeyGenAvatarGenerator:
    def __init__(self, api_key: Optional[str] = None, avatar_id: Optional[str] = None):
        """
        Initialize the HeyGen avatar generator
        
        Args:
            api_key: HeyGen API key. If None, will use HEYGEN_API_KEY environment variable
            avatar_id: Default avatar ID to use. If None, will use HEYGEN_AVATAR_ID environment variable
        """
        self.api_key = api_key or os.getenv('HEYGEN_API_KEY')
        self.avatar_id = avatar_id or os.getenv('HEYGEN_AVATAR_ID')
        
        if not self.api_key:
            logger.warning("HeyGen API key not provided. Avatar generation will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
        
        self.base_url = "https://api.heygen.com/v2"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def is_enabled(self) -> bool:
        """
        Check if avatar generation is enabled (API key available)
        
        Returns:
            True if enabled, False otherwise
        """
        return self.enabled
    
    def generate_avatar_video(self, 
                            script_text: str, 
                            avatar_id: Optional[str] = None,
                            voice_id: Optional[str] = None,
                            background: str = "office") -> Dict[str, Any]:
        """
        Generate an avatar reaction video based on the script
        
        Args:
            script_text: Text for the avatar to speak
            avatar_id: Avatar ID to use (defaults to instance avatar_id)
            voice_id: Voice ID to use (optional)
            background: Background scene (default: "office")
            
        Returns:
            Dictionary containing generation results
        """
        if not self.enabled:
            return self._get_disabled_response()
        
        try:
            logger.info(f"Generating avatar video with script length: {len(script_text)} chars")
            
            # Use provided avatar_id or fall back to instance default
            used_avatar_id = avatar_id or self.avatar_id
            if not used_avatar_id:
                raise ValueError("Avatar ID is required. Set HEYGEN_AVATAR_ID environment variable or pass avatar_id parameter.")
            
            # Prepare the request payload
            payload = {
                "video_inputs": [
                    {
                        "character": {
                            "type": "avatar",
                            "avatar_id": used_avatar_id,
                            "avatar_style": "normal"
                        },
                        "voice": {
                            "type": "text",
                            "input_text": script_text,
                            "voice_id": voice_id or "1bd001e7e50f421d891986aad5158bc8",  # Default English voice
                            "speed": 1.0
                        },
                        "background": {
                            "type": "color",
                            "value": "#ffffff"
                        }
                    }
                ],
                "dimension": {
                    "width": 1280,
                    "height": 720
                },
                "aspect_ratio": "16:9"
            }
            
            # Make the API request to generate video
            response = requests.post(
                f"{self.base_url}/video/generate",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result_data = response.json()
                video_id = result_data.get("data", {}).get("video_id")
                
                if video_id:
                    logger.info(f"Video generation initiated. Video ID: {video_id}")
                    return {
                        "success": True,
                        "video_id": video_id,
                        "status": "generating",
                        "message": "Avatar video generation started",
                        "error": None
                    }
                else:
                    raise ValueError("No video ID returned from API")
            else:
                error_msg = f"HeyGen API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return self._get_error_response(error_msg)
                
        except Exception as e:
            logger.error(f"Avatar video generation failed: {str(e)}")
            return self._get_error_response(str(e))
    
    def check_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation job
        
        Args:
            video_id: The video ID to check
            
        Returns:
            Dictionary containing status information
        """
        if not self.enabled:
            return self._get_disabled_response()
        
        try:
            logger.info(f"Checking status for video ID: {video_id}")
            
            response = requests.get(
                f"{self.base_url}/video/{video_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                result_data = response.json()
                data = result_data.get("data", {})
                
                status = data.get("status", "unknown")
                video_url = data.get("video_url")
                
                return {
                    "success": True,
                    "video_id": video_id,
                    "status": status,
                    "video_url": video_url,
                    "duration": data.get("duration"),
                    "thumbnail_url": data.get("thumbnail_url"),
                    "error": None
                }
            else:
                error_msg = f"Status check failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return self._get_error_response(error_msg)
                
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return self._get_error_response(str(e))
    
    def wait_for_completion(self, video_id: str, max_wait_time: int = 300, poll_interval: int = 10) -> Dict[str, Any]:
        """
        Wait for video generation to complete
        
        Args:
            video_id: The video ID to wait for
            max_wait_time: Maximum time to wait in seconds (default: 300)
            poll_interval: How often to check status in seconds (default: 10)
            
        Returns:
            Dictionary containing final video information
        """
        if not self.enabled:
            return self._get_disabled_response()
        
        logger.info(f"Waiting for video completion: {video_id}")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status_result = self.check_video_status(video_id)
            
            if not status_result.get("success"):
                return status_result
            
            status = status_result.get("status")
            
            if status == "completed":
                logger.info(f"Video generation completed: {video_id}")
                return status_result
            elif status == "failed":
                return self._get_error_response("Video generation failed")
            elif status in ["generating", "pending"]:
                logger.info(f"Video still generating... Status: {status}")
                time.sleep(poll_interval)
            else:
                logger.warning(f"Unknown status: {status}")
                time.sleep(poll_interval)
        
        # Timeout reached
        return self._get_error_response(f"Video generation timed out after {max_wait_time} seconds")
    
    def generate_reaction_script(self, feedback_data: Dict[str, Any]) -> str:
        """
        Generate a script for the avatar based on feedback data
        
        Args:
            feedback_data: Feedback data from GPT (score, emojis, comment)
            
        Returns:
            Script text for the avatar to speak
        """
        score = feedback_data.get("score", 5.0)
        comment = feedback_data.get("comment", "Interesting argument!")
        emojis = feedback_data.get("emojis", "🤔")
        
        # Create a more natural speaking script
        if score >= 8.0:
            intro = "Wow! That was impressive!"
        elif score >= 6.0:
            intro = "Not bad, not bad!"
        elif score >= 4.0:
            intro = "Hmm, I see what you're trying to say..."
        else:
            intro = "Okay, let me be honest with you..."
        
        # Clean up the comment for speech
        clean_comment = comment.replace("...", " pause ").replace("!", " exclamation ")
        
        script = f"{intro} {clean_comment} I'm giving you a {score} out of 10 for that argument!"
        
        return script
    
    def create_reaction_video(self, feedback_data: Dict[str, Any], avatar_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a complete reaction video based on feedback
        
        Args:
            feedback_data: Feedback data from GPT
            avatar_id: Avatar ID to use (optional)
            
        Returns:
            Dictionary containing video generation results
        """
        if not self.enabled:
            return self._get_disabled_response()
        
        try:
            script = self.generate_reaction_script(feedback_data)
            logger.info(f"Generated reaction script: {script}")
            
            return self.generate_avatar_video(script, avatar_id)
            
        except Exception as e:
            logger.error(f"Reaction video creation failed: {str(e)}")
            return self._get_error_response(str(e))
    
    def _get_disabled_response(self) -> Dict[str, Any]:
        """Get response when avatar generation is disabled"""
        return {
            "success": False,
            "video_id": None,
            "status": "disabled",
            "video_url": None,
            "message": "Avatar generation is disabled. Add HeyGen API key to enable.",
            "error": "HeyGen API key not configured"
        }
    
    def _get_error_response(self, error_message: str) -> Dict[str, Any]:
        """Get error response format"""
        return {
            "success": False,
            "video_id": None,
            "status": "error",
            "video_url": None,
            "message": "Avatar video generation failed",
            "error": error_message
        }
    
    def get_sample_video_url(self) -> str:
        """
        Get a sample video URL for testing when HeyGen is not available
        
        Returns:
            Sample video URL
        """
        return "https://www.w3schools.com/html/mov_bbb.mp4"

def test_avatar_generation():
    """
    Test function for the avatar generation module
    """
    try:
        generator = HeyGenAvatarGenerator()
        
        if not generator.is_enabled():
            print("HeyGen is not enabled (no API key). Testing disabled mode...")
            result = generator.generate_avatar_video("Test script")
            print(f"Disabled result: {result}")
            return
        
        # Test with sample feedback
        sample_feedback = {
            "score": 7.5,
            "emojis": "🔥💯✨",
            "comment": "Solid points! You're getting warmed up!",
            "reasoning": "Good structure and clear examples"
        }
        
        print("Testing avatar generation...")
        result = generator.create_reaction_video(sample_feedback)
        print(f"Generation result: {result}")
        
        if result.get("success") and result.get("video_id"):
            print(f"Video ID: {result['video_id']}")
            print("Checking status...")
            status = generator.check_video_status(result["video_id"])
            print(f"Status: {status}")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_avatar_generation()