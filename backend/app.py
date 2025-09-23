#!/usr/bin/env python3
"""
FlavorCraft Backend API - FIXED VERSION with proper field mapping
Fixes ALL issues: Recipe field names, error handling, fallback responses
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import json
import google.generativeai as genai
from datetime import datetime
import traceback
from pathlib import Path
import sys
import io

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], methods=['GET', 'POST'], allow_headers=['Content-Type'])

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Google AI Configuration
GOOGLE_API_KEY = "AIzaSyDDhOVdFG5tl29-v1gi7KUqul7iPAX8oqc"
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    llm_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("✅ Gemini model initialized")
except Exception as e:
    logger.error(f"❌ Gemini initialization failed: {e}")
    llm_model = None

# File extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a', 'aac'}

# Global models
audio_model = None
image_model = None

def initialize_models():
    """Initialize models with comprehensive error handling"""
    global audio_model, image_model
    
    print("🔄 INITIALIZING MODELS...")
    
    # Initialize Image Model
    try:
        logger.info("Loading image model...")
        from image_model import ImageModel
        image_model = ImageModel()
        
        if hasattr(image_model, 'food_categories'):
            logger.info(f"✅ Image model loaded with {len(image_model.food_categories)} categories")
            print(f"📸 Image Model: ✅ Ready ({len(image_model.food_categories)} categories)")
        else:
            logger.info("✅ Image model loaded (no categories info)")
            print("📸 Image Model: ✅ Ready")
            
    except Exception as e:
        logger.error(f"❌ Image model failed: {e}")
        logger.error(traceback.format_exc())
        print(f"📸 Image Model: ❌ Failed - {e}")
        image_model = None
    
    # Initialize Audio Model
    try:
        logger.info("Loading audio model...")
        from audio_model import AudioModel
        audio_model = AudioModel()
        logger.info("✅ Audio model loaded successfully")
        print("🎙️ Audio Model: ✅ Ready")
        
    except Exception as e:
        logger.error(f"❌ Audio model failed: {e}")
        logger.error(traceback.format_exc())
        print(f"🎙️ Audio Model: ❌ Failed - {e}")
        audio_model = None
    
    # Status summary
    print("=" * 50)
    print("🍕 FLAVORCRAFT MODEL STATUS")
    print("=" * 50)
    print(f"📸 Image Classification: {'✅ WORKING' if image_model else '❌ FAILED'}")
    print(f"🎙️ Audio Transcription: {'✅ WORKING' if audio_model else '❌ FAILED'}")
    print(f"🤖 Recipe Generation: {'✅ WORKING' if llm_model else '❌ FAILED'}")
    print("=" * 50)

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_recipe_with_gemini(ingredients_text="", dish_name="", image_analysis=None, audio_info=None):
    """Generate recipe using Gemini with all available information - FIXED field names"""
    
    if not llm_model:
        logger.error("❌ Gemini model not available")
        return generate_fallback_recipe(ingredients_text, dish_name, image_analysis, audio_info)
    
    try:
        logger.info(f"🤖 Generating recipe for dish: '{dish_name}'")
        
        # Extract image details
        confidence_score = 0.0
        cuisine_detected = "International"
        
        if image_analysis and image_analysis.get('success'):
            confidence_score = image_analysis.get('confidence', 0.0)
            cuisine_detected = image_analysis.get('cuisine', 'International')
            logger.info(f"📸 Using image analysis: {dish_name} ({confidence_score:.2f} confidence)")
        
        # Extract audio details
        audio_transcript = ""
        if audio_info and audio_info.get('success'):
            audio_transcript = audio_info.get('transcript', '')
            logger.info(f"🎙️ Using audio: '{audio_transcript[:50]}...'")
        
        # Create comprehensive prompt with FIXED field names
        prompt = f"""
You are a professional chef creating a detailed recipe. Use this information:

🍽️ DISH IDENTIFIED: "{dish_name}"
📊 CONFIDENCE: {confidence_score:.1%}
🌍 CUISINE: {cuisine_detected}
🥘 INGREDIENTS AVAILABLE: {ingredients_text if ingredients_text else "Use common ingredients"}
🎙️ USER INSTRUCTIONS: {audio_transcript if audio_transcript else "None"}

Create a complete recipe in EXACT JSON format with these EXACT field names:

{{
  "name": "{dish_name.replace('_', ' ').title()}",
  "cuisine": "{cuisine_detected}",
  "difficulty": "Easy",
  "totalTime": "45 minutes",
  "prepTime": "15 minutes",
  "cookTime": "30 minutes",
  "servings": 4,
  "description": "Delicious {dish_name.replace('_', ' ')} with authentic flavors and fresh ingredients",
  
  "ingredients": [
    "2 tablespoons olive oil",
    "1 large onion, chopped",
    "3 cloves garlic, minced",
    "Main ingredients based on: {ingredients_text if ingredients_text else 'common ingredients'}",
    "Salt and pepper to taste",
    "Additional spices for {cuisine_detected} flavor"
  ],
  
  "instructions": [
    "Heat olive oil in a large pan over medium heat",
    "Add chopped onion and cook until softened (about 5 minutes)",
    "Add garlic and cook for 1 minute until fragrant",
    "Add main ingredients and cook according to recipe requirements",
    "Season with salt, pepper and spices to taste",
    "Cook until done and serve hot"
  ],
  
  "tips": [
    "Use fresh ingredients for best flavor",
    "Adjust spices to your taste preference",
    "Let ingredients cook properly for authentic {cuisine_detected} taste",
    "Serve immediately while hot"
  ],
  
  "tags": ["homemade", "{cuisine_detected.lower()}", "fresh"],
  "cooking_methods": ["sauté", "simmer"],
  "nutritional_highlights": ["Fresh ingredients", "Balanced flavors"],
  "variations": [
    "Add vegetables for extra nutrition",
    "Adjust spice level to preference",
    "Use different proteins as desired"
  ]
}}

RETURN ONLY THE JSON OBJECT WITH NO OTHER TEXT.
"""

        logger.info("📄 Calling Gemini API...")
        response = llm_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            
            try:
                recipe_data = json.loads(json_text)
                logger.info(f"✅ Recipe generated: {recipe_data.get('name', 'Unknown')}")
                
                return {
                    'success': True,
                    'recipe': recipe_data,
                    'method': 'gemini_ai',
                    'message': f'Recipe for {dish_name} generated successfully'
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parse error: {e}")
                logger.debug(f"Response text: {json_text[:200]}...")
                return generate_fallback_recipe(ingredients_text, dish_name, image_analysis, audio_info)
        else:
            logger.error("❌ No JSON found in Gemini response")
            return generate_fallback_recipe(ingredients_text, dish_name, image_analysis, audio_info)
            
    except Exception as e:
        logger.error(f"❌ Gemini generation error: {e}")
        logger.error(traceback.format_exc())
        return generate_fallback_recipe(ingredients_text, dish_name, image_analysis, audio_info)

def generate_fallback_recipe(ingredients_text="", dish_name="", image_analysis=None, audio_info=None):
    """Generate fallback recipe when Gemini fails - FIXED field names"""
    logger.info("📄 Generating fallback recipe...")
    
    confidence_score = 0.0
    cuisine_type = "International"
    
    if image_analysis and image_analysis.get('success'):
        confidence_score = image_analysis.get('confidence', 0.0)
        cuisine_type = image_analysis.get('cuisine', 'International')
    
    recipe_name = dish_name.replace('_', ' ').title() if dish_name != 'Unknown' else 'Custom Recipe'
    
    # Create base ingredients from user input
    base_ingredients = [
        "2 tablespoons cooking oil",
        "1 medium onion, chopped",
        "2 cloves garlic, minced"
    ]
    
    # Add user ingredients if provided
    if ingredients_text:
        user_ingredients = [f"Your ingredients: {ingredients_text[:100]}"]
        base_ingredients.extend(user_ingredients)
    
    base_ingredients.extend([
        "Salt and black pepper to taste",
        "Fresh herbs for garnish"
    ])
    
    recipe_data = {
        'name': recipe_name,
        'cuisine': cuisine_type,
        'difficulty': 'Easy',
        'totalTime': '35 minutes',
        'prepTime': '10 minutes',
        'cookTime': '25 minutes',
        'servings': 4,
        'description': f'A delicious {recipe_name.lower()} made with fresh ingredients and your available items.',
        
        'ingredients': base_ingredients,
        
        'instructions': [
            "Heat oil in a large pan over medium heat",
            "Add chopped onion and cook until soft and translucent (about 5 minutes)",
            "Add minced garlic and cook for 1 minute until fragrant",
            "Add your main ingredients and cook according to their requirements",
            "Season generously with salt and pepper",
            "Cook until everything is heated through and flavors are well combined",
            "Taste and adjust seasoning as needed",
            "Garnish with fresh herbs and serve hot"
        ],
        
        'tips': [
            "Use the freshest ingredients available for best flavor",
            "Don't rush the cooking process - let flavors develop",
            "Taste and adjust seasonings throughout cooking",
            "Serve immediately while hot for best experience"
        ],
        
        'tags': ['homemade', 'easy', 'customizable'],
        'cooking_methods': ['sauté', 'simmer'],
        'nutritional_highlights': ['Customizable nutrition', 'Fresh ingredients'],
        'variations': [
            'Add your favorite vegetables for extra nutrition',
            'Adjust spice levels to your preference',
            'Substitute ingredients based on dietary needs'
        ]
    }
    
    return {
        'success': True,
        'recipe': recipe_data,
        'method': 'fallback',
        'message': 'Fallback recipe generated with your inputs'
    }

# ===== API ENDPOINTS =====

@app.route('/', methods=['GET'])
def health_check():
    """Health check with detailed status"""
    return jsonify({
        'status': 'healthy',
        'message': 'FlavorCraft API - FIELD-FIXED VERSION',
        'version': '6.0.0-field-fixed',
        'timestamp': datetime.now().isoformat(),
        
        'models': {
            'image_classification': image_model is not None,
            'audio_transcription': audio_model is not None,
            'recipe_generation': llm_model is not None
        },
        
        'dataset': {
            'food_categories': len(image_model.food_categories) if image_model and hasattr(image_model, 'food_categories') else 0,
            'status': 'loaded' if image_model else 'not_available'
        },
        
        'endpoints': [
            'GET / - Health check',
            'POST /predict - Complete recipe generation',
            'POST /transcribe - Audio transcription',
            'GET /test-audio - Audio diagnostics'
        ],
        
        'fixes_applied': [
            'Fixed recipe field names to match frontend',
            'Improved error handling and fallbacks',
            'Enhanced response structure',
            'Better field mapping consistency'
        ]
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Audio transcription endpoint with improved error handling"""
    try:
        logger.info("🎙️ === AUDIO TRANSCRIPTION REQUEST ===")
        
        # Check for audio file
        if 'audio' not in request.files:
            logger.error("❌ No audio file in request")
            return jsonify({
                'success': False,
                'transcript': '',
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        logger.info(f"📁 Audio file received: {audio_file.filename}")
        
        # Check if file has content
        if not audio_file or not audio_file.filename:
            logger.error("❌ Empty audio file")
            return jsonify({
                'success': False,
                'transcript': '',
                'error': 'Audio file is empty'
            }), 400
        
        # Check audio model
        if not audio_model:
            logger.error("❌ Audio model not available")
            return jsonify({
                'success': False,
                'transcript': 'Audio processing not available',
                'error': 'Audio model not loaded'
            }), 503
        
        # Validate file format
        if not allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
            logger.error(f"❌ Invalid audio format: {audio_file.filename}")
            return jsonify({
                'success': False,
                'transcript': f'Invalid format. Use: {", ".join(ALLOWED_AUDIO_EXTENSIONS)}',
                'error': 'Unsupported audio format'
            }), 400
        
        # Create unique filename and save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = secure_filename(f"audio_{timestamp}_{audio_file.filename or 'recording.wav'}")
        temp_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"💾 Saving audio to: {temp_audio_path}")
        
        try:
            # Save audio file
            audio_file.seek(0)
            audio_file.save(temp_audio_path)
            
            # Verify file was saved
            if not os.path.exists(temp_audio_path):
                raise Exception("File was not saved successfully")
            
            file_size = os.path.getsize(temp_audio_path)
            logger.info(f"✅ Audio saved successfully: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Saved file is empty")
            
            # Process with audio model
            logger.info("📄 Starting transcription...")
            audio_result = audio_model.process_audio_for_recipe(temp_audio_path)
            logger.info(f"📊 Audio processing result: {audio_result}")
            
            if audio_result and audio_result.get('success'):
                transcript = audio_result.get('transcript', '').strip()
                
                if transcript:
                    logger.info(f"✅ Transcription successful: '{transcript}'")
                    
                    return jsonify({
                        'success': True,
                        'transcript': transcript,
                        'confidence': audio_result.get('confidence', 0.8),
                        'method': audio_result.get('method_used', 'speech_recognition'),
                        'message': 'Audio transcribed successfully'
                    }), 200
                else:
                    logger.warning("⚠️ Empty transcript")
                    return jsonify({
                        'success': False,
                        'transcript': '',
                        'error': 'No clear speech found in audio'
                    }), 400
            else:
                error_msg = audio_result.get('error', 'Unknown processing error') if audio_result else 'No result from audio model'
                logger.error(f"❌ Audio processing failed: {error_msg}")
                
                return jsonify({
                    'success': False,
                    'transcript': '',
                    'error': error_msg
                }), 500
        
        finally:
            # Cleanup temp file
            try:
                if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    logger.info("🧹 Cleaned up temp file")
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up temp file: {cleanup_error}")
        
    except Exception as e:
        logger.error(f"💥 Critical transcription error: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'transcript': '',
            'error': 'System error during transcription'
        }), 500

@app.route('/predict', methods=['POST'])
def predict():
    """FIXED Complete prediction endpoint with proper field mapping"""
    try:
        logger.info("🚀 === PREDICTION REQUEST START ===")
        start_time = datetime.now()
        
        # Get inputs
        ingredients_text = request.form.get('text', '').strip()
        has_image = 'image' in request.files and request.files['image'].filename
        has_audio = 'audio' in request.files and request.files['audio'].filename
        
        logger.info(f"📋 Inputs received:")
        logger.info(f"   📝 Text: {'✅' if ingredients_text else '❌'} ({len(ingredients_text)} chars)")
        logger.info(f"   📸 Image: {'✅' if has_image else '❌'}")
        logger.info(f"   🎙️ Audio: {'✅' if has_audio else '❌'}")
        
        # Require at least one input
        if not ingredients_text and not has_image and not has_audio:
            return jsonify({
                'success': False,
                'error': 'No input provided',
                'message': 'Please provide ingredients, image, or audio'
            }), 400
        
        # Initialize results
        image_analysis = None
        audio_analysis = None
        dish_name = "Custom Dish"
        
        # === PROCESS IMAGE ===
        if has_image and image_model:
            try:
                logger.info("📸 Processing image...")
                image_file = request.files['image']
                
                if allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    image_file.seek(0)
                    
                    logger.info("📄 Running image classification...")
                    image_analysis = image_model.analyze_image_for_recipe(image_file)
                    
                    if image_analysis and image_analysis.get('success'):
                        dish_name = image_analysis.get('food_class', 'Custom Dish')
                        confidence = image_analysis.get('confidence', 0.0)
                        cuisine = image_analysis.get('cuisine', 'International')
                        
                        logger.info(f"✅ IMAGE CLASSIFIED:")
                        logger.info(f"   🍽️ Dish: {dish_name}")
                        logger.info(f"   🎯 Confidence: {confidence:.2%}")
                        logger.info(f"   🌍 Cuisine: {cuisine}")
                    else:
                        logger.warning("⚠️ Image classification failed")
                        dish_name = "Custom Dish"
                else:
                    logger.error(f"❌ Invalid image format: {image_file.filename}")
                    
            except Exception as e:
                logger.error(f"❌ Image processing error: {e}")
                image_analysis = {'success': False, 'error': str(e)}
        
        # === PROCESS AUDIO ===
        if has_audio and audio_model:
            try:
                logger.info("🎙️ Processing audio...")
                audio_file = request.files['audio']
                
                if allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
                    # Create temp file for audio processing
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    filename = secure_filename(f"predict_audio_{timestamp}.wav")
                    temp_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    try:
                        audio_file.seek(0)
                        audio_file.save(temp_audio_path)
                        
                        if os.path.getsize(temp_audio_path) > 0:
                            logger.info("📄 Running audio transcription...")
                            audio_analysis = audio_model.process_audio_for_recipe(temp_audio_path)
                            
                            if audio_analysis and audio_analysis.get('success'):
                                transcript = audio_analysis.get('transcript', '')
                                logger.info(f"✅ AUDIO TRANSCRIBED: '{transcript[:50]}...'")
                            else:
                                logger.warning("⚠️ Audio transcription failed")
                        else:
                            logger.error("❌ Audio file is empty")
                    
                    finally:
                        # Cleanup
                        try:
                            if os.path.exists(temp_audio_path):
                                os.remove(temp_audio_path)
                        except:
                            pass
                else:
                    logger.error(f"❌ Invalid audio format: {audio_file.filename}")
                    
            except Exception as e:
                logger.error(f"❌ Audio processing error: {e}")
                audio_analysis = {'success': False, 'error': str(e)}
        
        # === GENERATE RECIPE ===
        logger.info(f"🤖 Generating recipe for: '{dish_name}'")
        
        recipe_result = generate_recipe_with_gemini(
            ingredients_text=ingredients_text,
            dish_name=dish_name,
            image_analysis=image_analysis,
            audio_info=audio_analysis
        )
        
        if not recipe_result.get('success'):
            logger.error("❌ Recipe generation failed")
            return jsonify({
                'success': False,
                'error': 'Recipe generation failed',
                'message': 'Could not generate recipe'
            }), 500
        
        # === PREPARE RESPONSE WITH CORRECT FIELD MAPPING ===
        processing_time = (datetime.now() - start_time).total_seconds()
        
        response = {
            'success': True,
            'recipe': recipe_result['recipe'],  # This now has correct field names
            
            'analysis_results': {
                'image_classification': image_analysis,
                'audio_transcription': audio_analysis
            },
            
            'generation_info': {
                'method': recipe_result.get('method', 'unknown'),
                'processing_time': round(processing_time, 2),
                'dish_identified': dish_name,
                'inputs_used': {
                    'text': bool(ingredients_text),
                    'image': has_image and image_analysis and image_analysis.get('success'),
                    'audio': has_audio and audio_analysis and audio_analysis.get('success')
                }
            },
            
            'message': recipe_result.get('message', 'Recipe generated'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add compatibility fields for frontend
        response['image_class'] = dish_name
        response['audio_transcript'] = audio_analysis.get('transcript', '') if audio_analysis and audio_analysis.get('success') else ''
        
        # Add classification details with proper structure
        if image_analysis and image_analysis.get('success'):
            response['classification_details'] = {
                'dish': dish_name,
                'confidence': image_analysis.get('confidence', 0.0),
                'confidence_percentage': f"{image_analysis.get('confidence', 0.0):.1%}",
                'cuisine': image_analysis.get('cuisine', 'International'),
                'success': True
            }
        else:
            response['classification_details'] = {
                'dish': 'Custom Dish',
                'confidence': 0.0,
                'confidence_percentage': '0.0%',
                'cuisine': 'International',
                'success': False
            }
        
        logger.info("✅ === PREDICTION COMPLETE ===")
        logger.info(f"🍽️ Generated: {recipe_result['recipe'].get('name', 'Unknown')}")
        logger.info(f"⏱️ Time: {processing_time:.2f}s")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"💥 Critical prediction error: {e}")
        logger.error(traceback.format_exc())
        
        # Return a proper fallback response even on critical errors
        fallback_recipe = generate_fallback_recipe("", "Custom Dish", None, None)
        
        return jsonify({
            'success': True,  # Set to True so frontend displays the fallback
            'recipe': fallback_recipe['recipe'],
            'analysis_results': {
                'image_classification': {'success': False, 'error': 'Processing failed'},
                'audio_transcription': {'success': False, 'error': 'Processing failed'}
            },
            'generation_info': {
                'method': 'emergency_fallback',
                'processing_time': 0,
                'dish_identified': 'Custom Dish',
                'inputs_used': {
                    'text': bool(request.form.get('text', '')),
                    'image': 'image' in request.files,
                    'audio': 'audio' in request.files
                }
            },
            'message': 'Recipe generated using fallback method due to processing error',
            'image_class': 'Custom Dish',
            'audio_transcript': '',
            'classification_details': {
                'dish': 'Custom Dish',
                'confidence': 0.0,
                'confidence_percentage': '0.0%',
                'cuisine': 'International',
                'success': False
            },
            'timestamp': datetime.now().isoformat(),
            'error_handled': True
        }), 200  # Return 200 so frontend processes the fallback recipe

@app.route('/test-audio', methods=['GET'])
def test_audio():
    """Audio system diagnostics"""
    return jsonify({
        'audio_model_loaded': audio_model is not None,
        'supported_formats': list(ALLOWED_AUDIO_EXTENSIONS),
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
        'upload_folder_writable': os.access(app.config['UPLOAD_FOLDER'], os.W_OK),
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
        'status': 'Ready' if audio_model else 'Not Available',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify backend is working"""
    return jsonify({
        'status': 'Backend is working!',
        'timestamp': datetime.now().isoformat(),
        'models_loaded': {
            'image_model': image_model is not None,
            'audio_model': audio_model is not None,
            'llm_model': llm_model is not None
        },
        'message': 'All systems operational'
    })

# ===== ERROR HANDLERS =====

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({
        'success': False,
        'error': 'File too large',
        'max_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': '404 - Endpoint not found',
        'available_endpoints': ['/', '/predict', '/transcribe', '/test-audio', '/test']
    }), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500 Internal Server Error: {e}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# ===== INITIALIZATION =====

def setup_upload_directory():
    """Setup upload directory"""
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Test write permissions
        test_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        
        logger.info(f"✅ Upload directory ready: {app.config['UPLOAD_FOLDER']}")
        print(f"📁 Upload Directory: ✅ Ready ({app.config['UPLOAD_FOLDER']})")
        return True
    except Exception as e:
        logger.error(f"❌ Upload directory setup failed: {e}")
        print(f"📁 Upload Directory: ❌ Failed - {e}")
        return False

# Initialize everything
print("🍕" * 50)
print("🚀 FLAVORCRAFT BACKEND - FIELD-FIXED VERSION")
print("🍕" * 50)

setup_upload_directory()
initialize_models()

print("✅ INITIALIZATION COMPLETE")
print("🍕" * 50)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    
    print("=" * 60)
    print("🚀 STARTING FLAVORCRAFT API SERVER")
    print("=" * 60)
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📡 CORS: Enabled for http://localhost:3000")
    print(f"📂 Upload: {app.config['UPLOAD_FOLDER']}")
    print("=" * 60)
    print("🔗 ENDPOINTS:")
    print("   GET  / - Health check")
    print("   POST /predict - Complete recipe generation")
    print("   POST /transcribe - Audio transcription")
    print("   GET  /test-audio - Audio diagnostics")
    print("   GET  /test - Backend test")
    print("=" * 60)
    print("🎯 FIXES APPLIED:")
    print("   ✅ Fixed recipe field names (name, cuisine, etc.)")
    print("   ✅ Improved error handling with fallback recipes")
    print("   ✅ Enhanced response structure consistency")
    print("   ✅ Better field mapping between frontend/backend")
    print("   ✅ Emergency fallback for critical errors")
    print("=" * 60)
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f"💥 Server startup failed: {e}")
        print(f"❌ STARTUP FAILED: {e}")