from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import logging
from werkzeug.utils import secure_filename
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm', 'm4a', 'aac'}

# Initialize models with error handling
audio_model = None
image_model = None
text_model = None

# Try to load text model (should work with basic dependencies)
try:
    from text_model import TextModel
    text_model = TextModel()
    logger.info("Text model initialized successfully")
except Exception as e:
    logger.warning(f"Text model initialization failed: {str(e)}")

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

def combine_all_inputs(text_input, audio_transcript, image_class, image_cuisine):
    """Combine text, audio transcript, and image classification into comprehensive input"""
    combined_text = ""
    
    # Start with original text input
    if text_input and text_input.strip():
        combined_text += text_input.strip() + "\n\n"
    
    # Add audio transcript
    if audio_transcript and audio_transcript.strip():
        combined_text += f"Voice instructions: {audio_transcript.strip()}\n\n"
    
    # Add image-based information
    if image_class and image_class != 'Unknown':
        combined_text += f"Dish type: {image_class.replace('_', ' ')}\n"
    
    if image_cuisine and image_cuisine != 'Unknown' and image_cuisine != 'International':
        combined_text += f"Cuisine style: {image_cuisine}\n"
    
    return combined_text.strip()

def generate_enhanced_recipe(text_input="", audio_analysis=None, image_analysis=None):
    """Generate recipe using all available inputs with enhanced logic"""
    
    # Extract information from different sources
    audio_transcript = ""
    if audio_analysis and audio_analysis.get('success'):
        audio_transcript = audio_analysis.get('transcript', '')
    
    image_class = 'Unknown'
    image_cuisine = 'International'
    image_confidence = 0
    
    if image_analysis and image_analysis.get('success'):
        image_class = image_analysis.get('food_class', 'Unknown')
        image_cuisine = image_analysis.get('cuisine', 'International')
        image_confidence = image_analysis.get('confidence', 0)
    
    # Combine all text inputs
    combined_input = combine_all_inputs(text_input, audio_transcript, image_class, image_cuisine)
    
    # Use enhanced text model if available
    if text_model and combined_input:
        try:
            result = text_model.generate_complete_recipe(
                combined_input, 
                cuisine_hint=image_cuisine if image_cuisine != 'International' else None,
                image_class=image_class if image_class != 'Unknown' else None
            )
            
            if result.get('success'):
                recipe_data = result['analysis']
                
                # Enhance recipe name with image information
                if image_class != 'Unknown' and image_confidence > 0.3:
                    recipe_data['name'] = image_class.replace('_', ' ').title() + " Recipe"
                
                # Override cuisine if image detection is confident
                if image_cuisine != 'International' and image_confidence > 0.5:
                    recipe_data['cuisine'] = image_cuisine
                
                # Add analysis metadata
                recipe_data['analysis_metadata'] = {
                    'has_text_input': bool(text_input and text_input.strip()),
                    'has_audio_input': bool(audio_transcript),
                    'has_image_input': bool(image_class != 'Unknown'),
                    'image_confidence': image_confidence,
                    'combined_input_length': len(combined_input)
                }
                
                return {
                    'success': True,
                    'recipe': recipe_data,
                    'message': 'Recipe generated successfully using enhanced AI analysis'
                }
        except Exception as e:
            logger.error(f"Enhanced recipe generation failed: {str(e)}")
    
    # Fallback recipe generation
    return generate_fallback_recipe(text_input, audio_transcript, image_class, image_cuisine)

def generate_fallback_recipe(text_input="", audio_transcript="", image_class="Unknown", image_cuisine="International"):
    """Generate a fallback recipe when enhanced generation fails"""
    
    # Determine recipe name
    recipe_name = "Generated Recipe"
    if image_class and image_class != 'Unknown':
        recipe_name = image_class.replace('_', ' ').title() + " Recipe"
    elif any(word in (text_input + audio_transcript).lower() for word in ['chicken', 'beef', 'fish']):
        for protein in ['chicken', 'beef', 'fish', 'pork']:
            if protein in (text_input + audio_transcript).lower():
                recipe_name = f"{protein.title()} Recipe"
                break
    
    # Determine cuisine
    cuisine = image_cuisine if image_cuisine != 'International' else 'International'
    
    # Enhanced ingredients based on inputs
    ingredients = ["2 tbsp olive oil", "1 medium onion, chopped", "2 cloves garlic, minced"]
    
    # Add ingredients based on text analysis
    all_text = (text_input + " " + audio_transcript).lower()
    
    # Common ingredients detection
    ingredient_mapping = {
        'chicken': '1 lb chicken breast, cut into pieces',
        'beef': '1 lb beef, cubed',
        'fish': '1 lb fish fillets',
        'tomato': '2 large tomatoes, diced',
        'rice': '1 cup basmati rice',
        'pasta': '12 oz pasta',
        'coconut milk': '1 can coconut milk',
        'ginger': '1 inch fresh ginger, minced',
        'curry': '2 tsp curry powder',
        'cumin': '1 tsp ground cumin',
        'turmeric': '1/2 tsp turmeric',
        'cilantro': '1/4 cup fresh cilantro, chopped',
        'lemon': '2 tbsp fresh lemon juice',
        'soy sauce': '3 tbsp soy sauce'
    }
    
    for keyword, ingredient in ingredient_mapping.items():
        if keyword in all_text:
            ingredients.append(ingredient)
    
    # Add salt and pepper
    ingredients.append("Salt and pepper to taste")
    
    # Generate cuisine-specific ingredients
    if cuisine == 'Indian':
        if not any('curry' in ing for ing in ingredients):
            ingredients.extend(['1 tsp garam masala', '1 tsp ground coriander'])
    elif cuisine == 'Italian':
        if not any('tomato' in ing for ing in ingredients):
            ingredients.extend(['1 can crushed tomatoes', '1 tbsp fresh basil'])
    elif cuisine == 'Chinese':
        if not any('soy sauce' in ing for ing in ingredients):
            ingredients.extend(['2 tbsp soy sauce', '1 tsp sesame oil'])
    
    # Generate instructions based on cuisine and ingredients
    instructions = ["Heat olive oil in a large pan over medium heat"]
    
    if any('onion' in ing for ing in ingredients):
        instructions.append("Add chopped onion and cook until softened, about 5 minutes")
    
    if any('garlic' in ing for ing in ingredients):
        instructions.append("Add minced garlic and cook for 1 minute until fragrant")
    
    # Add main ingredient cooking
    main_proteins = ['chicken', 'beef', 'fish']
    has_protein = any(protein in ing.lower() for ing in ingredients for protein in main_proteins)
    
    if has_protein:
        instructions.append("Add the protein and cook until browned on all sides")
    
    # Add cuisine-specific steps
    if cuisine == 'Indian':
        instructions.extend([
            "Add spices and cook until fragrant, about 1 minute",
            "Add tomatoes and cook until they break down",
            "Simmer covered for 15-20 minutes until tender",
            "Garnish with fresh cilantro and serve with rice"
        ])
    elif cuisine == 'Italian':
        instructions.extend([
            "Add tomatoes and herbs",
            "Simmer for 15-20 minutes until sauce thickens",
            "Season with salt and pepper",
            "Serve with pasta or bread"
        ])
    elif cuisine == 'Chinese':
        instructions.extend([
            "Add vegetables and stir-fry for 3-4 minutes",
            "Add soy sauce and other seasonings",
            "Stir-fry for another 2-3 minutes until everything is heated through",
            "Serve hot over rice"
        ])
    else:
        instructions.extend([
            "Add remaining ingredients and mix well",
            "Cook for 10-15 minutes until everything is heated through",
            "Season with salt and pepper to taste",
            "Serve hot and enjoy"
        ])
    
    # Generate cooking tips
    tips = ["Taste and adjust seasoning as you cook"]
    if cuisine == 'Indian':
        tips.append("Let spices bloom in oil for maximum flavor")
    elif cuisine == 'Italian':
        tips.append("Use fresh herbs when possible")
    elif cuisine == 'Chinese':
        tips.append("Keep heat high for proper stir-frying")
    
    recipe_data = {
        'name': recipe_name,
        'cuisine': cuisine,
        'difficulty': 'Medium',
        'servings': 4,
        'prep_time': '15 minutes',
        'cook_time': '25 minutes',
        'total_time': '40 minutes',
        'description': f'A delicious {cuisine.lower()} recipe created from your inputs, featuring fresh ingredients and authentic flavors.',
        'ingredients': ingredients,
        'instructions': instructions,
        'cooking_methods': ['sauté', 'simmer'],
        'tags': [cuisine.lower(), 'homemade', 'flavorful'],
        'tips': tips,
        'analysis_metadata': {
            'generation_method': 'fallback',
            'has_text_input': bool(text_input),
            'has_audio_input': bool(audio_transcript),
            'has_image_input': bool(image_class != 'Unknown'),
            'detected_cuisine': cuisine
        }
    }
    
    return {
        'success': True,
        'recipe': recipe_data,
        'message': 'Recipe generated using fallback method'
    }

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'FlavorCraft API is running',
        'models_loaded': {
            'audio': audio_model is not None,
            'image': image_model is not None,
            'text': text_model is not None
        }
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Enhanced main prediction endpoint"""
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
        text_analysis = None
        image_analysis = None
        audio_analysis = None
        
        # Process audio input first (to get transcript for text analysis)
        if has_audio and audio_model:
            try:
                audio_file = request.files['audio']
                if allowed_file(audio_file.filename, ALLOWED_AUDIO_EXTENSIONS):
                    filename = secure_filename(audio_file.filename)
                    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    audio_file.save(temp_path)
                    
                    try:
                        audio_analysis = audio_model.process_audio_for_recipe(temp_path)
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
                    logger.info("Image analysis completed successfully")
            except Exception as e:
                logger.error(f"Image analysis failed: {str(e)}")
        
        # Generate enhanced recipe using all inputs
        recipe_result = generate_enhanced_recipe(text_input, audio_analysis, image_analysis)
        
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
                'text': text_analysis,
                'image': image_analysis,
                'audio': audio_analysis
            },
            'message': recipe_result.get('message', 'Recipe generated successfully')
        }
        
        # Add compatibility fields for frontend
        response['text_summary'] = recipe_data.get('description', '')
        response['image_class'] = image_analysis.get('food_class', 'Unknown') if image_analysis and image_analysis.get('success') else 'Unknown'
        response['audio_transcript'] = audio_analysis.get('transcript', '') if audio_analysis and audio_analysis.get('success') else ''
        
        logger.info("Enhanced recipe generated successfully")
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
    """Enhanced text analysis endpoint"""
    try:
        if not text_model:
            return jsonify({
                'success': False,
                'error': 'Text model not available'
            }), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        # Use the enhanced recipe generation
        result = text_model.generate_complete_recipe(data['text'])
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
    
    port = int(os.environ.get('PORT', 5005))
    
    logger.info(f"Starting Enhanced FlavorCraft API on port {port}")
    logger.info(f"Models available - Text: {text_model is not None}, Audio: {audio_model is not None}, Image: {image_model is not None}")
    
    app.run(host='0.0.0.0', port=port, debug=True)