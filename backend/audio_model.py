import speech_recognition as sr
import io
import wave
import numpy as np
from pydub import AudioSegment
import tempfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioModel:
    def __init__(self):
        """Initialize the audio processing model with speech recognition"""
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def preprocess_audio(self, audio_file):
        """
        Preprocess audio file for better speech recognition
        Convert to WAV format and optimize for speech recognition
        """
        try:
            # Load audio file using pydub
            audio = AudioSegment.from_file(audio_file)
            
            # Convert to mono if stereo
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate to 16kHz (optimal for speech recognition)
            audio = audio.set_frame_rate(16000)
            
            # Normalize audio volume
            audio = audio.normalize()
            
            # Apply noise reduction (simple high-pass filter)
            audio = audio.high_pass_filter(300)
            
            # Export to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                audio.export(temp_file.name, format="wav")
                return temp_file.name
                
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_file):
        """
        Transcribe audio file to text using speech recognition
        Supports multiple recognition engines with fallback
        """
        transcript = ""
        preprocessed_file = None
        
        try:
            # Preprocess the audio file
            preprocessed_file = self.preprocess_audio(audio_file)
            if not preprocessed_file:
                return "Error: Could not process audio file"
            
            # Load the audio file
            with sr.AudioFile(preprocessed_file) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record the audio data
                audio_data = self.recognizer.record(source)
            
            # Try Google Web Speech API first (most accurate)
            try:
                transcript = self.recognizer.recognize_google(audio_data, language='en-US')
                logger.info("Successfully transcribed using Google Web Speech API")
                
            except sr.RequestError:
                # Fallback to Sphinx (offline)
                try:
                    transcript = self.recognizer.recognize_sphinx(audio_data)
                    logger.info("Successfully transcribed using Sphinx (offline)")
                    
                except sr.RequestError:
                    transcript = "Error: Could not request results from speech recognition service"
                    
            except sr.UnknownValueError:
                transcript = "Could not understand audio clearly. Please speak more clearly."
                
        except Exception as e:
            logger.error(f"Error in transcription: {str(e)}")
            transcript = f"Error processing audio: {str(e)}"
            
        finally:
            # Clean up temporary file
            if preprocessed_file and os.path.exists(preprocessed_file):
                try:
                    os.unlink(preprocessed_file)
                except:
                    pass
                    
        return transcript
    
    def extract_recipe_keywords(self, transcript):
        """
        Extract cooking-related keywords and phrases from transcript
        """
        cooking_keywords = [
            'cook', 'bake', 'fry', 'boil', 'steam', 'grill', 'roast', 'sauté',
            'chop', 'dice', 'slice', 'mix', 'blend', 'whisk', 'stir', 'fold',
            'season', 'marinate', 'simmer', 'broil', 'garnish', 'serve',
            'ingredient', 'recipe', 'dish', 'meal', 'cuisine', 'flavor',
            'spice', 'herb', 'salt', 'pepper', 'oil', 'butter', 'garlic',
            'onion', 'tomato', 'chicken', 'beef', 'fish', 'vegetable'
        ]
        
        found_keywords = []
        transcript_lower = transcript.lower()
        
        for keyword in cooking_keywords:
            if keyword in transcript_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def analyze_cooking_instructions(self, transcript):
        """
        Analyze transcript for cooking instructions and return structured data
        """
        analysis = {
            'transcript': transcript,
            'keywords': self.extract_recipe_keywords(transcript),
            'cooking_methods': [],
            'ingredients_mentioned': [],
            'time_references': [],
            'confidence': 'medium'
        }
        
        # Extract cooking methods
        cooking_methods = ['bake', 'fry', 'boil', 'steam', 'grill', 'roast', 'sauté', 'simmer']
        for method in cooking_methods:
            if method in transcript.lower():
                analysis['cooking_methods'].append(method)
        
        # Extract common ingredients
        common_ingredients = ['chicken', 'beef', 'fish', 'rice', 'pasta', 'tomato', 'onion', 'garlic', 'butter', 'oil']
        for ingredient in common_ingredients:
            if ingredient in transcript.lower():
                analysis['ingredients_mentioned'].append(ingredient)
        
        # Extract time references (simple pattern matching)
        import re
        time_patterns = [
            r'\d+\s*(?:minutes?|mins?)',
            r'\d+\s*(?:hours?|hrs?)',
            r'\d+\s*(?:seconds?|secs?)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            analysis['time_references'].extend(matches)
        
        # Determine confidence based on cooking keywords found
        if len(analysis['keywords']) > 5:
            analysis['confidence'] = 'high'
        elif len(analysis['keywords']) > 2:
            analysis['confidence'] = 'medium'
        else:
            analysis['confidence'] = 'low'
            
        return analysis
    
    def process_audio_for_recipe(self, audio_file):
        """
        Complete audio processing pipeline for recipe generation
        """
        try:
            # Transcribe the audio
            transcript = self.transcribe_audio(audio_file)
            
            if transcript.startswith("Error") or transcript.startswith("Could not"):
                return {
                    'success': False,
                    'transcript': transcript,
                    'analysis': None,
                    'error': transcript
                }
            
            # Analyze the transcript for recipe content
            analysis = self.analyze_cooking_instructions(transcript)
            
            return {
                'success': True,
                'transcript': transcript,
                'analysis': analysis,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error in audio processing pipeline: {str(e)}")
            return {
                'success': False,
                'transcript': "",
                'analysis': None,
                'error': str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    audio_model = AudioModel()
    
    # Test with a sample audio file (you would provide an actual audio file)
    # result = audio_model.process_audio_for_recipe("sample_recipe_audio.wav")
    # print(result)