import tensorflow as tf
import numpy as np
from PIL import Image
import io
import logging
from tensorflow.keras.applications import ResNet50, VGG16
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import requests
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageModel:
    def __init__(self):
        """Initialize the image classification model"""
        self.model = None
        self.food_categories = self.load_food_categories()
        self.cuisine_mapping = self.load_cuisine_mapping()
        self.load_model()
    
    def load_model(self):
        """Load pre-trained image classification model"""
        try:
            # Use ResNet50 pre-trained on ImageNet
            self.model = ResNet50(weights='imagenet')
            logger.info("Successfully loaded ResNet50 model")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Fallback to VGG16 if ResNet50 fails
            try:
                self.model = VGG16(weights='imagenet')
                logger.info("Successfully loaded VGG16 model as fallback")
            except Exception as e2:
                logger.error(f"Error loading fallback model: {str(e2)}")
                self.model = None
    
    def load_food_categories(self):
        """Load food categories and their cuisine mappings"""
        return {
            # Indian cuisine
            'naan': 'Indian', 'curry': 'Indian', 'biryani': 'Indian', 'dosa': 'Indian',
            'samosa': 'Indian', 'tikka': 'Indian', 'dal': 'Indian', 'roti': 'Indian',
            'tandoori': 'Indian', 'masala': 'Indian', 'vindaloo': 'Indian',
            
            # Italian cuisine
            'pizza': 'Italian', 'pasta': 'Italian', 'spaghetti': 'Italian', 'lasagna': 'Italian',
            'risotto': 'Italian', 'carbonara': 'Italian', 'bruschetta': 'Italian',
            'tiramisu': 'Italian', 'gelato': 'Italian', 'cappuccino': 'Italian',
            
            # Chinese cuisine
            'dumpling': 'Chinese', 'fried_rice': 'Chinese', 'noodles': 'Chinese',
            'spring_roll': 'Chinese', 'wonton': 'Chinese', 'chow_mein': 'Chinese',
            'dim_sum': 'Chinese', 'peking_duck': 'Chinese', 'sweet_and_sour': 'Chinese',
            
            # Japanese cuisine
            'sushi': 'Japanese', 'ramen': 'Japanese', 'tempura': 'Japanese',
            'miso_soup': 'Japanese', 'sashimi': 'Japanese', 'teriyaki': 'Japanese',
            'bento': 'Japanese', 'udon': 'Japanese', 'mochi': 'Japanese',
            
            # Mexican cuisine
            'taco': 'Mexican', 'burrito': 'Mexican', 'quesadilla': 'Mexican',
            'guacamole': 'Mexican', 'enchilada': 'Mexican', 'nachos': 'Mexican',
            'salsa': 'Mexican', 'tamales': 'Mexican', 'fajitas': 'Mexican',
            
            # American cuisine
            'burger': 'American', 'hot_dog': 'American', 'barbecue': 'American',
            'mac_and_cheese': 'American', 'fried_chicken': 'American',
            'apple_pie': 'American', 'pancake': 'American', 'donut': 'American',
            
            # French cuisine
            'croissant': 'French', 'baguette': 'French', 'crepe': 'French',
            'bouillabaisse': 'French', 'ratatouille': 'French', 'coq_au_vin': 'French',
            'souffle': 'French', 'macaron': 'French', 'escargot': 'French',
            
            # Thai cuisine
            'pad_thai': 'Thai', 'green_curry': 'Thai', 'tom_yum': 'Thai',
            'som_tam': 'Thai', 'massaman': 'Thai', 'spring_rolls': 'Thai',
            
            # Mediterranean cuisine
            'hummus': 'Mediterranean', 'falafel': 'Mediterranean', 'pita': 'Mediterranean',
            'greek_salad': 'Mediterranean', 'moussaka': 'Mediterranean',
            'baklava': 'Mediterranean', 'tzatziki': 'Mediterranean'
        }
    
    def load_cuisine_mapping(self):
        """Load detailed cuisine information"""
        return {
            'Indian': {
                'region': 'South Asian',
                'characteristics': ['Spicy', 'Aromatic', 'Complex spices', 'Rice/bread based'],
                'common_ingredients': ['cumin', 'turmeric', 'garam masala', 'ginger', 'garlic', 'chili'],
                'cooking_methods': ['curry', 'tandoor', 'tempering', 'slow cooking']
            },
            'Italian': {
                'region': 'European',
                'characteristics': ['Fresh ingredients', 'Tomato-based', 'Cheese', 'Herbs'],
                'common_ingredients': ['tomato', 'basil', 'garlic', 'olive oil', 'parmesan'],
                'cooking_methods': ['sautéing', 'slow simmering', 'wood-fired', 'fresh preparation']
            },
            'Chinese': {
                'region': 'East Asian',
                'characteristics': ['Wok cooking', 'Balance of flavors', 'Fresh vegetables', 'Rice/noodles'],
                'common_ingredients': ['soy sauce', 'ginger', 'garlic', 'scallions', 'sesame oil'],
                'cooking_methods': ['stir-frying', 'steaming', 'braising', 'deep-frying']
            },
            'Japanese': {
                'region': 'East Asian',
                'characteristics': ['Fresh ingredients', 'Minimal processing', 'Umami', 'Seasonal'],
                'common_ingredients': ['soy sauce', 'miso', 'rice vinegar', 'dashi', 'nori'],
                'cooking_methods': ['grilling', 'steaming', 'raw preparation', 'tempura']
            },
            'Mexican': {
                'region': 'North American',
                'characteristics': ['Spicy', 'Fresh herbs', 'Corn/beans', 'Bold flavors'],
                'common_ingredients': ['chili', 'lime', 'cilantro', 'avocado', 'tomato'],
                'cooking_methods': ['grilling', 'slow cooking', 'frying', 'fresh preparation']
            },
            'American': {
                'region': 'North American',
                'characteristics': ['Hearty portions', 'Comfort food', 'Grilled/fried', 'Sweet/savory'],
                'common_ingredients': ['beef', 'cheese', 'potatoes', 'corn', 'bacon'],
                'cooking_methods': ['grilling', 'frying', 'baking', 'barbecuing']
            },
            'French': {
                'region': 'European',
                'characteristics': ['Refined techniques', 'Butter/cream', 'Wine', 'Elegant presentation'],
                'common_ingredients': ['butter', 'cream', 'wine', 'herbs', 'cheese'],
                'cooking_methods': ['sautéing', 'braising', 'sauce-making', 'pastry']
            },
            'Thai': {
                'region': 'Southeast Asian',
                'characteristics': ['Balance of sweet/sour/salty/spicy', 'Fresh herbs', 'Coconut milk'],
                'common_ingredients': ['fish sauce', 'coconut milk', 'lemongrass', 'lime', 'chili'],
                'cooking_methods': ['stir-frying', 'curry making', 'steaming', 'grilling']
            },
            'Mediterranean': {
                'region': 'Mediterranean',
                'characteristics': ['Olive oil', 'Fresh vegetables', 'Herbs', 'Healthy fats'],
                'common_ingredients': ['olive oil', 'lemon', 'garlic', 'herbs', 'tomatoes'],
                'cooking_methods': ['grilling', 'roasting', 'fresh preparation', 'slow cooking']
            }
        }
    
    def preprocess_image(self, image_file):
        """
        Preprocess image for model prediction
        """
        try:
            # Load and resize image
            if isinstance(image_file, str):
                # If it's a file path
                img = Image.open(image_file)
            else:
                # If it's a file object
                img = Image.open(io.BytesIO(image_file.read()))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize to model input size
            img = img.resize((224, 224))
            
            # Convert to array and preprocess
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return None
    
    def classify_dish(self, image_file):
        """
        Classify the dish in the image
        """
        if self.model is None:
            return {
                'success': False,
                'predictions': [],
                'food_class': 'Unknown',
                'cuisine': 'Unknown',
                'confidence': 0.0,
                'error': 'Model not loaded'
            }
        
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_file)
            if processed_image is None:
                return {
                    'success': False,
                    'predictions': [],
                    'food_class': 'Unknown',
                    'cuisine': 'Unknown',
                    'confidence': 0.0,
                    'error': 'Image preprocessing failed'
                }
            
            # Make prediction
            predictions = self.model.predict(processed_image)
            decoded_predictions = decode_predictions(predictions, top=5)[0]
            
            # Find food-related predictions
            food_predictions = []
            best_food_match = None
            
            for pred in decoded_predictions:
                class_name = pred[1].lower()
                confidence = float(pred[2])
                
                # Check if prediction is food-related
                is_food = self.is_food_related(class_name)
                if is_food:
                    food_predictions.append({
                        'class': class_name,
                        'confidence': confidence,
                        'description': pred[1]
                    })
                    
                    if best_food_match is None:
                        best_food_match = class_name
            
            # Determine cuisine
            cuisine = self.determine_cuisine(best_food_match if best_food_match else decoded_predictions[0][1].lower())
            
            return {
                'success': True,
                'predictions': food_predictions if food_predictions else [
                    {
                        'class': decoded_predictions[0][1].lower(),
                        'confidence': float(decoded_predictions[0][2]),
                        'description': decoded_predictions[0][1]
                    }
                ],
                'food_class': best_food_match if best_food_match else decoded_predictions[0][1],
                'cuisine': cuisine,
                'confidence': food_predictions[0]['confidence'] if food_predictions else float(decoded_predictions[0][2]),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error in dish classification: {str(e)}")
            return {
                'success': False,
                'predictions': [],
                'food_class': 'Unknown',
                'cuisine': 'Unknown',
                'confidence': 0.0,
                'error': str(e)
            }
    
    def is_food_related(self, class_name):
        """
        Check if the predicted class is food-related
        """
        food_keywords = [
            'pizza', 'burger', 'sandwich', 'soup', 'salad', 'pasta', 'rice', 'bread',
            'chicken', 'fish', 'meat', 'vegetable', 'fruit', 'cake', 'pie', 'cookie',
            'ice_cream', 'coffee', 'tea', 'wine', 'beer', 'cheese', 'egg', 'milk',
            'curry', 'noodles', 'sushi', 'taco', 'hot_dog', 'french_fries', 'donut'
        ]
        
        return any(keyword in class_name for keyword in food_keywords)
    
    def determine_cuisine(self, food_class):
        """
        Determine the cuisine type based on the food class
        """
        # Direct mapping
        for food, cuisine in self.food_categories.items():
            if food in food_class.lower():
                return cuisine
        
        # Keyword-based mapping
        if any(word in food_class.lower() for word in ['curry', 'masala', 'biryani', 'naan']):
            return 'Indian'
        elif any(word in food_class.lower() for word in ['pizza', 'pasta', 'spaghetti']):
            return 'Italian'
        elif any(word in food_class.lower() for word in ['sushi', 'ramen', 'tempura']):
            return 'Japanese'
        elif any(word in food_class.lower() for word in ['taco', 'burrito', 'nachos']):
            return 'Mexican'
        elif any(word in food_class.lower() for word in ['burger', 'hot_dog', 'barbecue']):
            return 'American'
        elif any(word in food_class.lower() for word in ['dumpling', 'fried_rice', 'noodles']):
            return 'Chinese'
        elif any(word in food_class.lower() for word in ['pad_thai', 'green_curry']):
            return 'Thai'
        elif any(word in food_class.lower() for word in ['croissant', 'crepe', 'baguette']):
            return 'French'
        
        return 'International'
    
    def get_cuisine_info(self, cuisine):
        """
        Get detailed information about a cuisine
        """
        return self.cuisine_mapping.get(cuisine, {
            'region': 'Unknown',
            'characteristics': ['Diverse flavors'],
            'common_ingredients': ['Various'],
            'cooking_methods': ['Multiple techniques']
        })
    
    def analyze_image_for_recipe(self, image_file):
        """
        Complete image analysis pipeline for recipe generation
        """
        try:
            # Classify the dish
            classification_result = self.classify_dish(image_file)
            
            if not classification_result['success']:
                return classification_result
            
            # Get cuisine information
            cuisine_info = self.get_cuisine_info(classification_result['cuisine'])
            
            # Combine results
            result = classification_result.copy()
            result['cuisine_info'] = cuisine_info
            result['recipe_suggestions'] = self.generate_recipe_suggestions(
                classification_result['food_class'],
                classification_result['cuisine']
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in image analysis pipeline: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_recipe_suggestions(self, food_class, cuisine):
        """
        Generate recipe suggestions based on classified food and cuisine
        """
        suggestions = {
            'cooking_methods': [],
            'key_ingredients': [],
            'flavor_profile': [],
            'difficulty': 'Medium',
            'estimated_time': '30-45 minutes'
        }
        
        cuisine_info = self.get_cuisine_info(cuisine)
        suggestions['cooking_methods'] = cuisine_info.get('cooking_methods', [])
        suggestions['key_ingredients'] = cuisine_info.get('common_ingredients', [])
        suggestions['flavor_profile'] = cuisine_info.get('characteristics', [])
        
        # Adjust difficulty and time based on dish type
        if any(word in food_class.lower() for word in ['soup', 'curry', 'stew']):
            suggestions['difficulty'] = 'Medium'
            suggestions['estimated_time'] = '45-60 minutes'
        elif any(word in food_class.lower() for word in ['salad', 'sandwich']):
            suggestions['difficulty'] = 'Easy'
            suggestions['estimated_time'] = '15-30 minutes'
        elif any(word in food_class.lower() for word in ['cake', 'bread', 'pastry']):
            suggestions['difficulty'] = 'Hard'
            suggestions['estimated_time'] = '2-3 hours'
        
        return suggestions

# Example usage
if __name__ == "__main__":
    image_model = ImageModel()
    
    # Test with a sample image (you would provide an actual image file)
    # result = image_model.analyze_image_for_recipe("sample_food_image.jpg")
    # print(result)