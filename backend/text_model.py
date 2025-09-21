import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import logging
from collections import Counter
import json
import random

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextModel:
    def __init__(self):
        """Initialize the text processing model - now supporting LLM integration"""
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.cooking_terms = self.load_cooking_terms()
        self.ingredient_database = self.load_ingredient_database()
        self.cuisine_keywords = self.load_cuisine_keywords()
        
    def load_cooking_terms(self):
        """Load cooking methods and techniques"""
        return {
            'cooking_methods': [
                'bake', 'baking', 'baked', 'roast', 'roasting', 'roasted',
                'fry', 'frying', 'fried', 'sauté', 'sautéing', 'sautéed',
                'boil', 'boiling', 'boiled', 'steam', 'steaming', 'steamed',
                'grill', 'grilling', 'grilled', 'broil', 'broiling', 'broiled',
                'simmer', 'simmering', 'simmered', 'braise', 'braising', 'braised',
                'poach', 'poaching', 'poached', 'stir-fry', 'stir-fried',
                'deep-fry', 'deep-fried', 'pan-fry', 'pan-fried', 'blend', 'mix'
            ],
            'preparation_methods': [
                'chop', 'chopped', 'chopping', 'dice', 'diced', 'dicing',
                'slice', 'sliced', 'slicing', 'mince', 'minced', 'mincing',
                'grate', 'grated', 'grating', 'blend', 'blended', 'blending',
                'mix', 'mixed', 'mixing', 'whisk', 'whisked', 'whisking',
                'fold', 'folded', 'folding', 'knead', 'kneaded', 'kneading',
                'marinate', 'marinated', 'marinating', 'season', 'seasoned', 'seasoning'
            ],
            'measurements': [
                'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp',
                'pound', 'pounds', 'lb', 'lbs', 'ounce', 'ounces', 'oz',
                'gram', 'grams', 'g', 'kilogram', 'kilograms', 'kg',
                'liter', 'liters', 'l', 'milliliter', 'milliliters', 'ml',
                'pinch', 'dash', 'handful', 'piece', 'pieces', 'clove', 'cloves'
            ]
        }
    
    def load_ingredient_database(self):
        """Load common ingredients with categories"""
        return {
            'proteins': [
                'chicken', 'beef', 'pork', 'lamb', 'fish', 'salmon', 'tuna',
                'shrimp', 'prawns', 'crab', 'lobster', 'eggs', 'tofu',
                'beans', 'lentils', 'chickpeas', 'turkey', 'duck'
            ],
            'vegetables': [
                'onion', 'onions', 'garlic', 'tomato', 'tomatoes', 'carrot', 'carrots',
                'potato', 'potatoes', 'bell pepper', 'peppers', 'broccoli', 'spinach',
                'mushrooms', 'celery', 'ginger', 'lettuce', 'cucumber', 'zucchini',
                'eggplant', 'cauliflower', 'cabbage', 'corn', 'peas'
            ],
            'grains': [
                'rice', 'pasta', 'bread', 'flour', 'quinoa', 'noodles', 'wheat',
                'barley', 'oats', 'couscous', 'bulgur'
            ],
            'dairy': [
                'milk', 'cream', 'cheese', 'butter', 'yogurt', 'mozzarella',
                'parmesan', 'cheddar', 'feta', 'ricotta'
            ],
            'spices_herbs': [
                'salt', 'pepper', 'cumin', 'turmeric', 'paprika', 'oregano',
                'basil', 'thyme', 'rosemary', 'cilantro', 'parsley', 'mint',
                'cinnamon', 'cardamom', 'cloves', 'nutmeg', 'garam masala'
            ],
            'oils_fats': [
                'olive oil', 'vegetable oil', 'coconut oil', 'butter', 'ghee'
            ],
            'condiments': [
                'soy sauce', 'vinegar', 'lemon juice', 'lime juice', 'honey',
                'sugar', 'coconut milk', 'tomato sauce', 'hot sauce'
            ]
        }
    
    def load_cuisine_keywords(self):
        """Load cuisine-specific keywords"""
        return {
            'Indian': [
                'curry', 'masala', 'garam masala', 'turmeric', 'cumin', 'coriander',
                'cardamom', 'cinnamon', 'cloves', 'ghee', 'basmati', 'naan', 'tandoori',
                'biryani', 'dal', 'paneer', 'tikka', 'vindaloo', 'korma'
            ],
            'Italian': [
                'pasta', 'spaghetti', 'linguine', 'penne', 'lasagna', 'risotto',
                'parmesan', 'mozzarella', 'basil', 'oregano', 'tomato sauce',
                'olive oil', 'pizza', 'bruschetta', 'marinara', 'carbonara', 'pesto'
            ],
            'Chinese': [
                'soy sauce', 'ginger', 'garlic', 'scallions', 'sesame oil',
                'rice wine', 'hoisin sauce', 'oyster sauce', 'five spice',
                'bok choy', 'shiitake', 'stir fry', 'wok', 'noodles'
            ],
            'Mexican': [
                'chili', 'jalapeño', 'cilantro', 'lime', 'cumin', 'paprika',
                'avocado', 'beans', 'corn', 'tortilla', 'salsa', 'guacamole',
                'enchilada', 'quesadilla', 'taco', 'burrito'
            ],
            'Thai': [
                'coconut milk', 'lemongrass', 'thai basil', 'fish sauce',
                'lime leaves', 'galangal', 'pad thai', 'green curry', 'red curry'
            ]
        }

    def extract_ingredients_from_text(self, text):
        """Extract ingredients from text with improved parsing"""
        ingredients = []
        text_lower = text.lower()
        found_ingredients = set()
        
        # Look for ingredient lists (lines with bullets, dashes, or numbers)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or re.match(r'^\d+\.', line):
                clean_line = re.sub(r'^[-•*\d\.\s]+', '', line).strip()
                if clean_line and len(clean_line) > 2:
                    ingredients.append(clean_line)
        
        # If no structured list, extract from all categories
        if not ingredients:
            all_ingredients = []
            for category, items in self.ingredient_database.items():
                all_ingredients.extend(items)
            
            for ingredient in all_ingredients:
                if ingredient in text_lower and ingredient not in found_ingredients:
                    # Try to extract with context (quantity + ingredient)
                    pattern = rf'(\d+(?:\.\d+)?\s*(?:' + '|'.join(self.cooking_terms['measurements']) + r')?\s*)?' + re.escape(ingredient)
                    match = re.search(pattern, text_lower)
                    if match:
                        context = match.group(0)
                        ingredients.append(context.strip())
                        found_ingredients.add(ingredient)
        
        return ingredients[:10]  # Limit to 10 ingredients

    def extract_cooking_methods(self, text):
        """Extract cooking methods from text"""
        methods = []
        text_lower = text.lower()
        
        all_methods = self.cooking_terms['cooking_methods'] + self.cooking_terms['preparation_methods']
        
        for method in all_methods:
            if method in text_lower:
                methods.append(method)
        
        return list(set(methods))[:5]  # Remove duplicates, limit to 5

    def detect_cuisine(self, text):
        """Detect cuisine type from text"""
        text_lower = text.lower()
        cuisine_scores = {}
        
        for cuisine, keywords in self.cuisine_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                cuisine_scores[cuisine] = score
        
        if cuisine_scores:
            return max(cuisine_scores.items(), key=lambda x: x[1])[0]
        
        return 'International'

    def analyze_ingredients_text(self, text):
        """Analyze ingredients text and return structured data for LLM"""
        try:
            ingredients = self.extract_ingredients_from_text(text)
            cooking_methods = self.extract_cooking_methods(text)
            cuisine = self.detect_cuisine(text)
            
            # Extract any quantities or measurements
            quantities = []
            quantity_patterns = [
                r'\d+(?:\.\d+)?\s*(?:' + '|'.join(self.cooking_terms['measurements']) + r')',
                r'\d+(?:\.\d+)?',
                r'a handful of',
                r'a pinch of',
                r'to taste'
            ]
            
            for pattern in quantity_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                quantities.extend(matches)
            
            return {
                'success': True,
                'ingredients': ingredients,
                'cooking_methods': cooking_methods,
                'cuisine': cuisine,
                'quantities_found': quantities[:5],  # Limit to 5
                'text_length': len(text),
                'has_structured_list': any(line.strip().startswith(('-', '•', '*')) or re.match(r'^\d+\.', line.strip()) for line in text.split('\n')),
                'complexity_score': len(ingredients) + len(cooking_methods)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing ingredients text: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'ingredients': [],
                'cooking_methods': [],
                'cuisine': 'International'
            }

    def prepare_llm_context(self, ingredients_text, dish_name="", audio_transcript=""):
        """Prepare structured context for LLM processing"""
        
        context = {
            'ingredients_analysis': None,
            'dish_info': None,
            'audio_info': None,
            'combined_context': ""
        }
        
        # Analyze ingredients text
        if ingredients_text:
            context['ingredients_analysis'] = self.analyze_ingredients_text(ingredients_text)
        
        # Process dish name
        if dish_name and dish_name != 'Unknown':
            context['dish_info'] = {
                'name': dish_name,
                'cleaned_name': dish_name.replace('_', ' ').title(),
                'detected_cuisine': self.detect_cuisine_from_dish_name(dish_name)
            }
        
        # Process audio transcript
        if audio_transcript:
            context['audio_info'] = self.analyze_ingredients_text(audio_transcript)
            context['audio_info']['is_audio'] = True
        
        # Create combined context summary
        context['combined_context'] = self.create_combined_context(
            ingredients_text, dish_name, audio_transcript
        )
        
        return context

    def detect_cuisine_from_dish_name(self, dish_name):
        """Detect cuisine from dish name"""
        if not dish_name:
            return 'International'
        
        dish_lower = dish_name.lower()
        
        # Direct mappings for common dishes
        dish_cuisine_map = {
            'curry': 'Indian', 'biryani': 'Indian', 'masala': 'Indian',
            'pasta': 'Italian', 'pizza': 'Italian', 'risotto': 'Italian',
            'stir_fry': 'Chinese', 'fried_rice': 'Chinese', 'dumpling': 'Chinese',
            'sushi': 'Japanese', 'ramen': 'Japanese', 'tempura': 'Japanese',
            'taco': 'Mexican', 'burrito': 'Mexican', 'quesadilla': 'Mexican',
            'pad_thai': 'Thai', 'tom_yum': 'Thai', 'green_curry': 'Thai'
        }
        
        for dish, cuisine in dish_cuisine_map.items():
            if dish in dish_lower:
                return cuisine
        
        return 'International'

    def create_combined_context(self, ingredients_text, dish_name, audio_transcript):
        """Create a combined context summary for better LLM understanding"""
        
        context_parts = []
        
        if ingredients_text:
            context_parts.append(f"Ingredients/Recipe text: {ingredients_text[:200]}...")
        
        if dish_name and dish_name != 'Unknown':
            context_parts.append(f"Identified dish: {dish_name.replace('_', ' ')}")
        
        if audio_transcript:
            context_parts.append(f"Audio instructions: {audio_transcript[:100]}...")
        
        return " | ".join(context_parts)

    # Legacy methods for backward compatibility
    def analyze_recipe_text(self, text):
        """Legacy method - now redirects to ingredients analysis"""
        return self.analyze_ingredients_text(text)

    def generate_complete_recipe(self, text, cuisine_hint=None, image_class=None):
        """Legacy method - kept for backward compatibility"""
        analysis = self.analyze_ingredients_text(text)
        if analysis['success']:
            return {
                'success': True,
                'analysis': {
                    'ingredients': analysis['ingredients'],
                    'cooking_methods': analysis['cooking_methods'],
                    'cuisine': cuisine_hint or analysis['cuisine'],
                    'complexity': analysis['complexity_score']
                }
            }
        else:
            return analysis

# Example usage
if __name__ == "__main__":
    text_model = TextModel()
    
    # Test with sample ingredients
    sample_text = """
    Ingredients:
    - 2 lbs chicken breast
    - 1 large onion, chopped
    - 3 cloves garlic, minced
    - 1 inch ginger, minced
    - 2 tomatoes, diced
    - 1 can coconut milk
    - 2 tsp curry powder
    - 1 tsp turmeric
    - 1 tsp cumin
    - Salt and pepper to taste
    - Fresh cilantro for garnish
    
    I want to make a chicken curry
    """
    
    result = text_model.analyze_ingredients_text(sample_text)
    print(json.dumps(result, indent=2))