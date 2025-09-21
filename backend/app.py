from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import json
import google.generativeai as genai
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Configure Google AI
GOOGLE_API_KEY = "AIzaSyDDhOVdFG5tl29-v1gi7KUqul7iPAX8oqc"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
try:
    llm_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Google Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    llm_model = None

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a', 'aac'}

# Initialize models with error handling
audio_model = None
image_model = None

# Try to load audio model (may fail if speech recognition deps missing)
try:
    from audio_model import AudioModel
    audio_model = AudioModel()
    logger.info("Audio model initialized successfully")
except Exception as e:
    logger.warning(f"Audio model initialization failed: {str(e)}")

# Try to load image model (will likely fail without TensorFlow)
try:
    from image_model import ImageModel
    image_model = ImageModel()
    logger.info("Image model initialized successfully")
except Exception as e:
    logger.warning(f"Image model initialization failed: {str(e)}")

logger.info("Backend initialization completed")

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_recipe_with_llm(ingredients_text="", dish_name="", audio_transcript=""):
    """Generate recipe using Google Gemini LLM with the three inputs"""
    
    if not llm_model:
        logger.error("LLM model not available")
        return generate_fallback_recipe(ingredients_text, dish_name, audio_transcript)
    
    try:
        # Construct the prompt for the LLM
        prompt = f"""
You are a professional chef and recipe creator. Generate a detailed, delicious recipe based on the following inputs:

**Ingredients List:** {ingredients_text if ingredients_text else "Not provided"}

**Identified Dish:** {dish_name if dish_name and dish_name != 'Unknown' else "Not identified"}

**Audio Instructions:** {audio_transcript if audio_transcript else "Not provided"}

Please create a complete recipe with the following structure (respond in JSON format):

{{
  "name": "Recipe name",
  "cuisine": "Type of cuisine (e.g., Italian, Indian, Chinese, etc.)",
  "difficulty": "Easy/Medium/Hard",
  "prep_time": "X minutes",
  "cook_time": "X minutes",
  "total_time": "X minutes",
  "servings": 4,
  "description": "Brief appealing description of the dish",
  "ingredients": [
    "List of ingredients with quantities and preparation notes"
  ],
  "instructions": [
    "Step by step cooking instructions"
  ],
  "cooking_methods": ["sauté", "bake", "etc."],
  "tags": ["cuisine type", "difficulty", "meal type", etc.],
  "tips": [
    "Professional cooking tips for best results"
  ],
  "nutritional_highlights": ["Key nutritional benefits"],
  "variations": ["Possible recipe variations or substitutions"]
}}

Guidelines:
1. If ingredients are provided, use them as the base and add complementary ingredients
2. If a dish is identified from image, ensure the recipe matches that dish type
3. If audio instructions are provided, incorporate those cooking methods and preferences
4. Make realistic serving estimates and cooking times
5. Provide practical, achievable instructions
6. Include helpful cooking tips and possible variations
7. Ensure the recipe is complete and cookable

Focus on creating an authentic, delicious recipe that combines all the provided information coherently.
"""

        # Generate content using Gemini
        response = llm_model.generate_content(prompt)
        response_text = response.text
        
        # Try to extract JSON from the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = response_text[json_start:json_end]
            recipe_data = json.loads(json_text)
            
            # Validate and clean the recipe data
            validated_recipe = validate_recipe_data(recipe_data)
            
            return {
                'success': True,
                'recipe': validated_recipe,
                'generation_method': 'llm_gemini',
                'inputs_used': {
                    'has_ingredients': bool(ingredients_text),
                    'has_dish_name': bool(dish_name and dish_name != 'Unknown'),
                    'has_audio': bool(audio_transcript)
                },
                'message': 'Recipe generated successfully using Google Gemini AI'
            }
        else:
            logger.error("Failed to parse JSON from LLM response")
            return generate_fallback_recipe(ingredients_text, dish_name, audio_transcript)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return generate_fallback_recipe(ingredients_text, dish_name, audio_transcript)
    except Exception as e:
        logger.error(f"LLM generation error: {str(e)}")
        return generate_fallback_recipe(ingredients_text, dish_name, audio_transcript)

def validate_recipe_data(recipe_data):
    """Validate and clean recipe data from LLM"""
    validated = {
        'name': recipe_data.get('name', 'Generated Recipe'),
        'cuisine': recipe_data.get('cuisine', 'International'),
        'difficulty': recipe_data.get('difficulty', 'Medium'),
        'prep_time': recipe_data.get('prep_time', '15 minutes'),
        'cook_time': recipe_data.get('cook_time', '25 minutes'),
        'total_time': recipe_data.get('total_time', '40 minutes'),
        'servings': recipe_data.get('servings', 4),
        'description': recipe_data.get('description', 'A delicious homemade recipe'),
        'ingredients': recipe_data.get('ingredients', []),
        'instructions': recipe_data.get('instructions', []),
        'cooking_methods': recipe_data.get('cooking_methods', []),
        'tags': recipe_data.get('tags', []),
        'tips': recipe_data.get('tips', []),
        'nutritional_highlights': recipe_data.get('nutritional_highlights', []),
        'variations': recipe_data.get('variations', [])
    }
    
    # Ensure lists are not empty
    if not validated['ingredients']:
        validated['ingredients'] = ["Ingredients will be provided based on your inputs"]
    if not validated['instructions']:
        validated['instructions'] = ["Detailed instructions will be generated"]
    if not validated['tags']:
        validated['tags'] = ['homemade', validated['difficulty'].lower()]
    
    return validated

def generate_fallback_recipe(ingredients_text="", dish_name="", audio_transcript=""):
    """Generate a fallback recipe when LLM fails"""
    
    # Determine recipe name
    if dish_name and dish_name != 'Unknown':
        recipe_name = dish_name.replace('_', ' ').title() + " Recipe"
    elif ingredients_text and any(protein in ingredients_text.lower() for protein in ['chicken', 'beef', 'fish', 'pork']):
        for protein in ['chicken', 'beef', 'fish', 'pork']:
            if protein in ingredients_text.lower():
                recipe_name = f"{protein.title()} Recipe"
                break
    else:
        recipe_name = "Homemade Recipe"
    
    # Determine cuisine from dish name or ingredients
    cuisine = 'International'
    if dish_name:
        dish_lower = dish_name.lower()
        if any(word in dish_lower for word in ['curry', 'biryani', 'masala']):
            cuisine = 'Indian'
        elif any(word in dish_lower for word in ['pasta', 'pizza', 'risotto']):
            cuisine = 'Italian'
        elif any(word in dish_lower for word in ['stir_fry', 'noodles', 'dumpling']):
            cuisine = 'Chinese'
    
    # Basic fallback ingredients
    fallback_ingredients = [
        "2 tablespoons olive oil",
        "1 large onion, chopped", 
        "3 cloves garlic, minced",
        "1 lb main protein or vegetables",
        "1 can diced tomatoes (if applicable)",
        "Salt and pepper to taste",
        "Fresh herbs for garnish"
    ]
    
    # Basic instructions
    fallback_instructions = [
        "Heat olive oil in a large pan over medium heat",
        "Add chopped onion and cook until softened, about 5 minutes",
        "Add minced garlic and cook for 1 minute until fragrant",
        "Add your main ingredients and cook until properly done",
        "Season with salt and pepper to taste",
        "Garnish with fresh herbs and serve hot"
    ]
    
    recipe_data = {
        'name': recipe_name,
        'cuisine': cuisine,
        'difficulty': 'Medium',
        'prep_time': '15 minutes',
        'cook_time': '25 minutes',
        'total_time': '40 minutes',
        'servings': 4,
        'description': f'A delicious {cuisine.lower()} recipe made with fresh ingredients.',
        'ingredients': fallback_ingredients,
        'instructions': fallback_instructions,
        'cooking_methods': ['sauté', 'simmer'],
        'tags': [cuisine.lower(), 'homemade', 'medium'],
        'tips': [
            "Taste and adjust seasoning as you cook",
            "Use fresh ingredients for the best flavor",
            "Don't rush the cooking process"
        ],
        'nutritional_highlights': ['Homemade', 'Fresh ingredients'],
        'variations': ['Add your favorite vegetables', 'Try different spice combinations']
    }
    
    return {
        'success': True,
        'recipe': recipe_data,
        'generation_method': 'fallback',
        'message': 'Recipe generated using fallback method'
    }

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'FlavorCraft API is running with LLM integration',
        'models_loaded': {
            'audio': audio_model is not None,
            'image': image_model is not None,
            'llm': llm_model is not None
        },
        'llm_model': 'Google Gemini 1.5 Flash' if llm_model else 'Not available'
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint with LLM integration"""
    try:
        # Get inputs
        text_input = request.form.get('text', '').strip()
        has_image = 'image' in request.files and request.files['image'].filename
        has_audio = 'audio' in request.files and request.files['audio'].filename
        
        # Check if any input provided
        if not text_input and not has_image and not has_audio:
            return jsonify({
                'success': False,
                'error': 'No input provided. Please provide text, image, or audio.'
            }), 400
        
        logger.info(f"Processing request with: text={bool(text_input)}, image={has_image}, audio={has_audio}")
        
        # Initialize analysis results
        image_analysis = None
        audio_analysis = None
        dish_name = "Unknown"
        audio_transcript = ""
        
        # Process audio input
        if has_audio and audio_model:
            try:
                audio_file = request.files['audio']
                if allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
                    filename = secure_filename(audio_file.filename)
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    audio_file.save(temp_path)
                    
                    try:
                        audio_result = audio_model.process_audio_for_recipe(temp_path)
                        if audio_result.get('success'):
                            audio_analysis = audio_result
                            audio_transcript = audio_result.get('transcript', '')
                            logger.info("Audio analysis completed successfully")
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            except Exception as e:
                logger.error(f"Audio analysis failed: {str(e)}")
        
        # Process image input
        if has_image and image_model:
            try:
                image_file = request.files['image']
                if allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    image_analysis = image_model.analyze_image_for_recipe(image_file)
                    if image_analysis and image_analysis.get('success'):
                        dish_name = image_analysis.get('food_class', 'Unknown')
                        logger.info("Image analysis completed successfully")
            except Exception as e:
                logger.error(f"Image analysis failed: {str(e)}")
        
        # Generate recipe using LLM with all three inputs
        recipe_result = generate_recipe_with_llm(
            ingredients_text=text_input,
            dish_name=dish_name,
            audio_transcript=audio_transcript
        )
        
        if not recipe_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Failed to generate recipe',
                'message': 'Recipe generation failed'
            }), 500
        
        recipe_data = recipe_result['recipe']
        
        # Prepare comprehensive response
        response = {
            'success': True,
            'recipe': recipe_data,
            'analysis_results': {
                'image': image_analysis,
                'audio': audio_analysis
            },
            'generation_info': {
                'method': recipe_result.get('generation_method', 'unknown'),
                'inputs_used': recipe_result.get('inputs_used', {}),
                'llm_model': 'Google Gemini 1.5 Flash' if llm_model else 'Not available'
            },
            'message': recipe_result.get('message', 'Recipe generated successfully')
        }
        
        # Add compatibility fields for frontend
        response['text_summary'] = recipe_data.get('description', '')
        response['image_class'] = dish_name
        response['audio_transcript'] = audio_transcript
        
        logger.info("Recipe generated successfully using LLM")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in predict endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while processing your request'
        }), 500

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    """Text analysis endpoint using LLM"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        # Use LLM to generate recipe from text only
        result = generate_recipe_with_llm(ingredients_text=data['text'])
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze-text: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    """Audio analysis endpoint"""
    try:
        if not audio_model:
            return jsonify({
                'success': False,
                'error': 'Audio model not available. Speech recognition dependencies may be missing.',
                'transcript': 'Audio processing not available'
            })
        
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        filename = secure_filename(audio_file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        audio_file.save(temp_path)
        
        try:
            result = audio_model.process_audio_for_recipe(temp_path)
            return jsonify(result)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Error in analyze-audio: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'transcript': 'Error processing audio'
        })

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Image analysis endpoint"""
    try:
        if not image_model:
            return jsonify({
                'success': False,
                'error': 'Image model not available'
            }), 503
        
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        if not allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return jsonify({
                'success': False,
                'error': 'Invalid image file type'
            }), 400
        
        result = image_model.analyze_image_for_recipe(image_file)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in analyze-image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-recipe-llm', methods=['POST'])
def generate_recipe_llm_endpoint():
    """Direct LLM recipe generation endpoint"""
    try:
        data = request.get_json()
        
        ingredients = data.get('ingredients', '')
        dish_name = data.get('dish_name', '')
        audio_transcript = data.get('audio_transcript', '')
        
        result = generate_recipe_with_llm(ingredients, dish_name, audio_transcript)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in LLM endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'success': False, 'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    port = int(os.environ.get('PORT', 5007))
    
    logger.info(f"Starting FlavorCraft API with LLM integration on port {port}")
    logger.info(f"Models available - Audio: {audio_model is not None}, Image: {image_model is not None}, LLM: {llm_model is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=True)