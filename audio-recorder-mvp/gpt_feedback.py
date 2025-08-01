"""
GPT-4 Feedback Module
Handles argument scoring and feedback generation using OpenAI's GPT-4 API
"""

import os
import openai
import json
from typing import Optional, Dict, Any
import logging
from pydantic import BaseModel, Field

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArgumentFeedback(BaseModel):
    """Pydantic model for structured argument feedback"""
    score: float = Field(..., ge=1.0, le=10.0, description="Argument score from 1 to 10")
    emojis: str = Field(..., min_length=1, max_length=20, description="3-5 emojis representing reaction")
    comment: str = Field(..., max_length=100, description="Short emotional comment (max 20 words)")
    reasoning: Optional[str] = Field(None, description="Brief explanation of the score")

class GPTFeedbackGenerator:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the GPT feedback generator
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable
            model: GPT model to use (default: "gpt-4")
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # TikTok-style system prompt
        self.system_prompt = """You are a TikTok-style AI debate judge named "Mina" with a sassy, fun personality. 
The user just gave an argument and you need to react like you're in a viral TikTok video.

Your job:
1. Give a score from 1 to 10 (decimals allowed, e.g., 7.3)
2. Return 3-5 emojis that reflect your reaction
3. Provide a short, emotional comment (max 20 words)
4. Your tone should be expressive, fun, and viral-ready

Scoring Guidelines:
- 1-3: Terrible argument, no logic, makes no sense
- 4-5: Weak argument, some points but major flaws
- 6-7: Decent argument, has merit but could be stronger
- 8-9: Strong argument, well-reasoned and compelling
- 10: Perfect argument, unbeatable logic and presentation

Be authentic, use Gen Z language, and make it entertaining!

ALWAYS respond with valid JSON in this exact format:
{
  "score": 7.3,
  "emojis": "😏🤔💥",
  "comment": "Not bad... but you lost me halfway. Pick a side!",
  "reasoning": "Good opening but argument became unclear"
}"""

    def generate_feedback(self, argument_text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate feedback for an argument using GPT-4
        
        Args:
            argument_text: The transcribed argument text
            context: Optional context about the debate topic
            
        Returns:
            Dictionary containing feedback results
        """
        try:
            logger.info(f"Generating feedback for argument (length: {len(argument_text)} chars)")
            
            # Prepare the user message
            user_message = f"Argument: \"{argument_text}\""
            if context:
                user_message += f"\n\nContext: {context}"
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.8,  # More creative responses
                max_tokens=300,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse the response
            feedback_json = response.choices[0].message.content
            feedback_data = json.loads(feedback_json)
            
            # Validate the response using Pydantic
            feedback = ArgumentFeedback(**feedback_data)
            
            result = {
                "score": feedback.score,
                "emojis": feedback.emojis,
                "comment": feedback.comment,
                "reasoning": feedback.reasoning,
                "success": True,
                "error": None,
                "raw_response": feedback_json
            }
            
            logger.info(f"Feedback generated successfully. Score: {feedback.score}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._get_fallback_feedback("Invalid response format from AI")
            
        except Exception as e:
            logger.error(f"Feedback generation failed: {str(e)}")
            return self._get_fallback_feedback(str(e))
    
    def _get_fallback_feedback(self, error_message: str) -> Dict[str, Any]:
        """
        Generate fallback feedback when API fails
        
        Args:
            error_message: The error that occurred
            
        Returns:
            Dictionary with fallback feedback
        """
        fallback_responses = [
            {
                "score": 5.0,
                "emojis": "🤖😅🔧",
                "comment": "AI brain glitched! But I heard some good points.",
                "reasoning": "Technical difficulties occurred"
            },
            {
                "score": 6.0,
                "emojis": "⚡🤔💭",
                "comment": "Connection issues, but your passion came through!",
                "reasoning": "API error during evaluation"
            },
            {
                "score": 5.5,
                "emojis": "🌐😊👍",
                "comment": "Technical hiccup, but keep arguing!",
                "reasoning": "System error occurred"
            }
        ]
        
        import random
        fallback = random.choice(fallback_responses)
        
        return {
            **fallback,
            "success": False,
            "error": error_message,
            "raw_response": None
        }
    
    def generate_custom_feedback(self, argument_text: str, custom_prompt: str) -> Dict[str, Any]:
        """
        Generate feedback with a custom system prompt
        
        Args:
            argument_text: The transcribed argument text
            custom_prompt: Custom system prompt to use
            
        Returns:
            Dictionary containing feedback results
        """
        try:
            logger.info("Generating feedback with custom prompt")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": custom_prompt},
                    {"role": "user", "content": f"Argument: \"{argument_text}\""}
                ],
                temperature=0.8,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            feedback_json = response.choices[0].message.content
            feedback_data = json.loads(feedback_json)
            
            # Basic validation for custom prompts
            required_keys = ["score", "emojis", "comment"]
            for key in required_keys:
                if key not in feedback_data:
                    raise ValueError(f"Missing required key: {key}")
            
            result = {
                **feedback_data,
                "success": True,
                "error": None,
                "raw_response": feedback_json
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Custom feedback generation failed: {str(e)}")
            return self._get_fallback_feedback(str(e))
    
    def get_sample_feedback(self) -> Dict[str, Any]:
        """
        Get a sample feedback for testing purposes
        
        Returns:
            Dictionary with sample feedback
        """
        return {
            "score": 7.5,
            "emojis": "🔥💯✨",
            "comment": "Solid points! You're getting warmed up!",
            "reasoning": "Good structure and clear examples",
            "success": True,
            "error": None,
            "raw_response": '{"score": 7.5, "emojis": "🔥💯✨", "comment": "Solid points! You\'re getting warmed up!", "reasoning": "Good structure and clear examples"}'
        }

def test_feedback_generation():
    """
    Test function for the feedback generation module
    """
    try:
        generator = GPTFeedbackGenerator()
        
        # Test with sample arguments
        test_arguments = [
            "Pineapple on pizza is actually amazing because it adds a sweet contrast to the savory cheese and creates a perfect balance of flavors.",
            "Social media is ruining our generation because we're all addicted to likes and validation instead of real connections.",
            "Climate change is the biggest threat we face and everyone should go vegetarian to reduce carbon emissions."
        ]
        
        for i, argument in enumerate(test_arguments, 1):
            print(f"\n--- Test {i} ---")
            print(f"Argument: {argument}")
            
            result = generator.generate_feedback(argument)
            print(f"Success: {result['success']}")
            if result['success']:
                print(f"Score: {result['score']}")
                print(f"Emojis: {result['emojis']}")
                print(f"Comment: {result['comment']}")
                if result.get('reasoning'):
                    print(f"Reasoning: {result['reasoning']}")
            else:
                print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_feedback_generation()