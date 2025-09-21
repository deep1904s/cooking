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
        """Initialize the text processing model"""
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        self.cooking_terms = self.load_cooking_terms()
        self.ingredient_database = self.load_ingredient_database()
        self.cuisine_keywords = self.load_cuisine_keywords()
        self.recipe_templates = self.load_recipe_templates()
        
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
        """Load common ingredients with categories and default quantities"""
        return {
            'proteins': {
                'chicken': {'default_qty': '1 lb', 'prep': 'cut into pieces'},
                'beef': {'default_qty': '1 lb', 'prep': 'cut into cubes'},
                'pork': {'default_qty': '1 lb', 'prep': 'sliced'},
                'lamb': {'default_qty': '1 lb', 'prep': 'cut into chunks'},
                'fish': {'default_qty': '1 lb', 'prep': 'filleted'},
                'salmon': {'default_qty': '4 fillets', 'prep': 'skin removed'},
                'shrimp': {'default_qty': '1 lb', 'prep': 'peeled and deveined'},
                'eggs': {'default_qty': '4 large', 'prep': 'beaten'},
                'tofu': {'default_qty': '1 block', 'prep': 'cubed'},
                'beans': {'default_qty': '1 can', 'prep': 'drained and rinsed'},
                'lentils': {'default_qty': '1 cup', 'prep': 'dried'},
                'chickpeas': {'default_qty': '1 can', 'prep': 'drained'}
            },
            'vegetables': {
                'onion': {'default_qty': '1 large', 'prep': 'chopped'},
                'onions': {'default_qty': '2 medium', 'prep': 'chopped'},
                'garlic': {'default_qty': '3 cloves', 'prep': 'minced'},
                'tomato': {'default_qty': '2 large', 'prep': 'chopped'},
                'tomatoes': {'default_qty': '3 medium', 'prep': 'diced'},
                'carrot': {'default_qty': '2 large', 'prep': 'sliced'},
                'carrots': {'default_qty': '3 medium', 'prep': 'chopped'},
                'potato': {'default_qty': '4 medium', 'prep': 'cubed'},
                'potatoes': {'default_qty': '4 medium', 'prep': 'diced'},
                'bell pepper': {'default_qty': '1 large', 'prep': 'sliced'},
                'peppers': {'default_qty': '2 medium', 'prep': 'chopped'},
                'broccoli': {'default_qty': '1 head', 'prep': 'cut into florets'},
                'spinach': {'default_qty': '2 cups', 'prep': 'fresh'},
                'mushrooms': {'default_qty': '8 oz', 'prep': 'sliced'},
                'celery': {'default_qty': '2 stalks', 'prep': 'chopped'},
                'ginger': {'default_qty': '1 inch piece', 'prep': 'minced'}
            },
            'grains': {
                'rice': {'default_qty': '1 cup', 'prep': 'uncooked'},
                'pasta': {'default_qty': '12 oz', 'prep': 'any shape'},
                'bread': {'default_qty': '4 slices', 'prep': 'fresh'},
                'flour': {'default_qty': '2 cups', 'prep': 'all-purpose'},
                'quinoa': {'default_qty': '1 cup', 'prep': 'rinsed'},
                'noodles': {'default_qty': '8 oz', 'prep': 'dried'}
            },
            'dairy': {
                'milk': {'default_qty': '1 cup', 'prep': 'whole milk'},
                'cream': {'default_qty': '1/2 cup', 'prep': 'heavy cream'},
                'cheese': {'default_qty': '1 cup', 'prep': 'shredded'},
                'butter': {'default_qty': '2 tbsp', 'prep': 'unsalted'},
                'yogurt': {'default_qty': '1 cup', 'prep': 'plain'},
                'mozzarella': {'default_qty': '8 oz', 'prep': 'shredded'},
                'parmesan': {'default_qty': '1/2 cup', 'prep': 'grated'}
            },
            'spices_herbs': {
                'salt': {'default_qty': 'to taste', 'prep': ''},
                'pepper': {'default_qty': 'to taste', 'prep': 'black pepper'},
                'cumin': {'default_qty': '1 tsp', 'prep': 'ground'},
                'turmeric': {'default_qty': '1/2 tsp', 'prep': 'ground'},
                'garam masala': {'default_qty': '1 tsp', 'prep': ''},
                'basil': {'default_qty': '1 tbsp', 'prep': 'fresh, chopped'},
                'oregano': {'default_qty': '1 tsp', 'prep': 'dried'},
                'thyme': {'default_qty': '1 tsp', 'prep': 'fresh'},
                'cilantro': {'default_qty': '1/4 cup', 'prep': 'chopped'},
                'parsley': {'default_qty': '2 tbsp', 'prep': 'chopped'}
            },
            'oils_fats': {
                'olive oil': {'default_qty': '2 tbsp', 'prep': 'extra virgin'},
                'vegetable oil': {'default_qty': '2 tbsp', 'prep': ''},
                'coconut oil': {'default_qty': '1 tbsp', 'prep': ''},
                'ghee': {'default_qty': '1 tbsp', 'prep': ''}
            },
            'condiments': {
                'soy sauce': {'default_qty': '2 tbsp', 'prep': ''},
                'vinegar': {'default_qty': '1 tbsp', 'prep': 'white or apple cider'},
                'lemon juice': {'default_qty': '2 tbsp', 'prep': 'fresh'},
                'honey': {'default_qty': '1 tbsp', 'prep': ''},
                'sugar': {'default_qty': '1 tbsp', 'prep': 'white'},
                'coconut milk': {'default_qty': '1 can', 'prep': 'full-fat'}
            }
        }
    
    def load_cuisine_keywords(self):
        """Load cuisine-specific keywords"""
        return {
            'Indian': [
                'curry', 'masala', 'garam masala', 'turmeric', 'cumin', 'coriander',
                'cardamom', 'cinnamon', 'cloves', 'fenugreek', 'mustard seeds',
                'curry leaves', 'ghee', 'basmati', 'naan', 'chapati', 'tandoori',
                'biryani', 'dal', 'paneer', 'tikka', 'vindaloo', 'korma'
            ],
            'Italian': [
                'pasta', 'spaghetti', 'linguine', 'penne', 'lasagna', 'risotto',
                'parmesan', 'mozzarella', 'basil', 'oregano', 'tomato sauce',
                'olive oil', 'garlic', 'pizza', 'bruschetta', 'prosciutto',
                'marinara', 'carbonara', 'pesto'
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
    
    def load_recipe_templates(self):
        """Load recipe instruction templates for different cooking methods"""
        return {
            'sauté': [
                "Heat {oil} in a large pan over medium heat",
                "Add {aromatics} and cook until fragrant, about 2-3 minutes",
                "Add {main_ingredient} and cook until {cooking_indicator}",
                "Season with {seasonings} and serve"
            ],
            'curry': [
                "Heat {oil} in a heavy-bottomed pot",
                "Add {aromatics} and sauté until golden",
                "Add {spices} and cook until fragrant, about 1 minute",
                "Add {tomatoes} and cook until they break down",
                "Add {main_ingredient} and {liquid}",
                "Simmer covered for 15-20 minutes until tender",
                "Garnish with {herbs} and serve with rice"
            ],
            'pasta': [
                "Bring a large pot of salted water to boil",
                "Cook {pasta} according to package directions until al dente",
                "Meanwhile, heat {oil} in a large pan",
                "Add {aromatics} and cook until fragrant",
                "Add {other_ingredients} and cook briefly",
                "Drain pasta and add to the pan",
                "Toss with {cheese} and {herbs}, then serve"
            ],
            'stir_fry': [
                "Heat {oil} in a wok or large pan over high heat",
                "Add {aromatics} and stir-fry for 30 seconds",
                "Add {protein} and cook until nearly done",
                "Add {vegetables} and stir-fry until crisp-tender",
                "Add {sauce} and toss to combine",
                "Serve immediately over rice"
            ],
            'basic': [
                "Prepare all ingredients by {prep_method}",
                "Heat {cooking_fat} in a {cooking_vessel}",
                "Add {base_ingredients} and cook until {indicator}",
                "Season with {seasonings} to taste",
                "Serve hot and enjoy"
            ]
        }

    def extract_ingredients_from_text(self, text):
        """Enhanced ingredient extraction that handles quantities and creates structured list"""
        ingredients = []
        text_lower = text.lower()
        found_ingredients = set()
        
        # First, look for explicit ingredient lists (lines starting with - or numbers)
        lines = text.split('\n')
        ingredient_section = False
        
        for line in lines:
            line = line.strip()
            if re.match(r'^(ingredients?|shopping list)', line.lower()):
                ingredient_section = True
                continue
            elif re.match(r'^(instructions?|directions?|method|steps?)', line.lower()):
                ingredient_section = False
                continue
                
            if ingredient_section and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                # Clean the line
                clean_line = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if clean_line:
                    ingredients.append(clean_line)
                    # Extract the ingredient name for tracking
                    ingredient_name = self.extract_ingredient_name(clean_line)
                    if ingredient_name:
                        found_ingredients.add(ingredient_name)
        
        # If no structured list found, extract from free text
        if not ingredients:
            for category, items in self.ingredient_database.items():
                for ingredient_name, details in items.items():
                    if ingredient_name in text_lower and ingredient_name not in found_ingredients:
                        # Try to extract quantity from context
                        quantity = self.extract_quantity_for_ingredient(text, ingredient_name)
                        if quantity == "to taste":
                            quantity = details['default_qty']
                        
                        prep = details.get('prep', '')
                        if prep:
                            ingredients.append(f"{quantity} {ingredient_name}, {prep}")
                        else:
                            ingredients.append(f"{quantity} {ingredient_name}")
                        found_ingredients.add(ingredient_name)
        
        # Ensure we have at least some basic ingredients
        if len(ingredients) < 3:
            basic_ingredients = [
                "2 tbsp olive oil",
                "1 medium onion, chopped", 
                "2 cloves garlic, minced",
                "Salt and pepper to taste"
            ]
            
            for basic_ing in basic_ingredients:
                basic_name = basic_ing.split(',')[0].split()[-1]  # Get the ingredient name
                if not any(basic_name in ing.lower() for ing in ingredients):
                    ingredients.append(basic_ing)
        
        return ingredients[:15]  # Limit to 15 ingredients max

    def extract_ingredient_name(self, ingredient_line):
        """Extract the main ingredient name from a line"""
        # Remove quantities and measurements
        clean_line = re.sub(r'^\d+\.?\s*', '', ingredient_line)  # Remove numbers
        clean_line = re.sub(r'\b\d+(?:/\d+)?\s*(?:' + '|'.join(self.cooking_terms['measurements']) + r')\b', '', clean_line)
        clean_line = re.sub(r'^\d+(?:\.\d+)?\s*', '', clean_line)  # Remove leading numbers
        
        words = clean_line.split(',')[0].split()  # Take first part before comma
        if words:
            # Look for known ingredients
            for word in words:
                for category, items in self.ingredient_database.items():
                    if word.lower() in items:
                        return word.lower()
            return words[-1].lower()  # Return last word as ingredient name
        return None

    def generate_cooking_instructions(self, ingredients, cuisine, cooking_methods, text_input=""):
        """Generate detailed cooking instructions based on ingredients and methods"""
        instructions = []
        
        # Determine primary cooking method
        primary_method = 'basic'
        if cooking_methods:
            method = cooking_methods[0].lower()
            if any(curry_word in text_input.lower() for curry_word in ['curry', 'masala', 'dal']):
                primary_method = 'curry'
            elif any(pasta_word in method for pasta_word in ['pasta', 'spaghetti', 'noodles']):
                primary_method = 'pasta' 
            elif 'stir' in method or method in ['stir-fry', 'wok']:
                primary_method = 'stir_fry'
            elif method in ['sauté', 'fry', 'pan-fry']:
                primary_method = 'sauté'
        
        # Get template
        template = self.recipe_templates.get(primary_method, self.recipe_templates['basic'])
        
        # Identify ingredient categories from the ingredients list
        proteins = []
        vegetables = []
        aromatics = []
        spices = []
        liquids = []
        
        for ingredient in ingredients:
            ing_lower = ingredient.lower()
            if any(protein in ing_lower for protein in self.ingredient_database['proteins']):
                proteins.append(ingredient)
            elif any(veg in ing_lower for veg in ['onion', 'garlic', 'ginger']):
                aromatics.append(ingredient)
            elif any(veg in ing_lower for veg in self.ingredient_database['vegetables']):
                vegetables.append(ingredient)
            elif any(spice in ing_lower for spice in self.ingredient_database['spices_herbs']):
                spices.append(ingredient)
            elif 'milk' in ing_lower or 'broth' in ing_lower or 'stock' in ing_lower:
                liquids.append(ingredient)
        
        # Fill in template placeholders
        replacements = {
            '{oil}': 'oil' if not any('oil' in ing.lower() for ing in ingredients) else 'the oil',
            '{aromatics}': ', '.join(aromatics[:2]) if aromatics else 'onion and garlic',
            '{main_ingredient}': proteins[0] if proteins else 'main ingredients',
            '{cooking_indicator}': 'cooked through' if proteins else 'tender',
            '{seasonings}': 'salt and pepper',
            '{spices}': ', '.join(spices[:3]) if spices else 'spices',
            '{tomatoes}': 'tomatoes' if any('tomato' in ing.lower() for ing in ingredients) else 'canned tomatoes',
            '{liquid}': liquids[0] if liquids else 'water or broth',
            '{herbs}': 'fresh herbs',
            '{pasta}': 'pasta' if any('pasta' in ing.lower() for ing in ingredients) else 'noodles',
            '{cheese}': 'cheese' if any('cheese' in ing.lower() for ing in ingredients) else 'parmesan cheese',
            '{protein}': proteins[0] if proteins else 'protein',
            '{vegetables}': ', '.join(vegetables[:3]) if vegetables else 'vegetables',
            '{sauce}': 'sauce mixture',
            '{prep_method}': 'washing and chopping',
            '{cooking_fat}': 'oil',
            '{cooking_vessel}': 'large pan',
            '{base_ingredients}': aromatics[0] if aromatics else 'onion',
            '{indicator}': 'fragrant and softened'
        }
        
        # Generate instructions from template
        for template_instruction in template:
            instruction = template_instruction
            for placeholder, replacement in replacements.items():
                instruction = instruction.replace(placeholder, replacement)
            instructions.append(instruction)
        
        # Add cuisine-specific final touches
        if cuisine == 'Indian':
            instructions.append("Garnish with fresh cilantro and serve with basmati rice or naan bread")
        elif cuisine == 'Italian':
            instructions.append("Serve with fresh basil and grated Parmesan cheese")
        elif cuisine == 'Chinese':
            instructions.append("Garnish with chopped scallions and serve with steamed rice")
        elif cuisine == 'Mexican':
            instructions.append("Serve with fresh lime wedges and chopped cilantro")
        else:
            instructions.append("Taste and adjust seasoning before serving")
        
        return instructions

    def generate_complete_recipe(self, text_input, cuisine_hint=None, image_class=None):
        """Generate a complete recipe from text input"""
        try:
            if not text_input or len(text_input.strip()) < 3:
                return self.generate_fallback_recipe(cuisine_hint, image_class)
            
            # Basic analysis
            ingredients = self.extract_ingredients_from_text(text_input)
            cooking_methods = self.extract_cooking_methods(text_input)
            cuisine = cuisine_hint or self.detect_cuisine(text_input)
            servings = self.extract_servings(text_input)
            cooking_times = self.extract_cooking_time(text_input)
            
            # Generate recipe name
            recipe_name = self.generate_recipe_name(text_input, ingredients, cuisine, image_class)
            
            # Generate instructions
            instructions = self.generate_cooking_instructions(ingredients, cuisine, cooking_methods, text_input)
            
            # Calculate difficulty
            difficulty = self.calculate_difficulty(ingredients, cooking_methods, instructions)
            
            # Generate cooking times if not found
            if not cooking_times:
                if difficulty == 'Easy':
                    prep_time, cook_time = "10 minutes", "15 minutes"
                elif difficulty == 'Hard':
                    prep_time, cook_time = "25 minutes", "45 minutes" 
                else:
                    prep_time, cook_time = "15 minutes", "25 minutes"
            else:
                prep_time = cook_time = cooking_times[0] + " minutes"
            
            # Generate description
            description = self.generate_recipe_description(recipe_name, cuisine, ingredients[:3])
            
            return {
                'success': True,
                'analysis': {
                    'name': recipe_name,
                    'cuisine': cuisine,
                    'difficulty': difficulty,
                    'servings': servings,
                    'prep_time': prep_time,
                    'cook_time': cook_time,
                    'total_time': f"{int(prep_time.split()[0]) + int(cook_time.split()[0])} minutes",
                    'description': description,
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'cooking_methods': cooking_methods,
                    'tags': [cuisine.lower(), difficulty.lower(), 'homemade'],
                    'tips': self.generate_cooking_tips(cuisine, cooking_methods, ingredients)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating complete recipe: {str(e)}")
            return self.generate_fallback_recipe(cuisine_hint, image_class)

    def generate_recipe_name(self, text_input, ingredients, cuisine, image_class=None):
        """Generate an appropriate recipe name"""
        text_lower = text_input.lower()
        
        # Check if text already contains a recipe name
        if any(word in text_lower for word in ['recipe', 'dish', 'make', 'cook']):
            words = text_input.split()
            for i, word in enumerate(words):
                if word.lower() in ['recipe', 'dish'] and i > 0:
                    potential_name = ' '.join(words[:i]).title()
                    if len(potential_name) > 3:
                        return potential_name + " Recipe"
        
        # Use image classification if available
        if image_class and image_class != 'Unknown':
            return image_class.replace('_', ' ').title() + " Recipe"
        
        # Generate name based on main ingredients and cuisine
        main_ingredients = []
        for ing in ingredients[:3]:
            ingredient_name = ing.split(',')[0].split()[-1]
            if len(ingredient_name) > 3:
                main_ingredients.append(ingredient_name.title())
        
        if main_ingredients:
            if cuisine != 'International':
                return f"{cuisine} {main_ingredients[0]} Dish"
            else:
                return f"{main_ingredients[0]} Recipe"
        
        return f"{cuisine} Recipe" if cuisine != 'International' else "Homemade Recipe"

    def generate_recipe_description(self, name, cuisine, main_ingredients):
        """Generate a recipe description"""
        descriptions = [
            f"A delicious {cuisine.lower()} dish that combines {', '.join([ing.split(',')[0].split()[-1] for ing in main_ingredients])} with aromatic spices and fresh ingredients.",
            f"This {cuisine.lower()} recipe brings together the perfect balance of flavors and textures in every bite.",
            f"A traditional {cuisine.lower()} preparation that's both satisfying and full of authentic flavors.",
            f"Experience the rich taste of {cuisine.lower()} cuisine with this carefully crafted recipe."
        ]
        
        if cuisine == 'International':
            descriptions = [
                f"A flavorful dish that combines {', '.join([ing.split(',')[0].split()[-1] for ing in main_ingredients])} with carefully selected seasonings.",
                "This recipe brings together fresh ingredients and time-tested cooking techniques for a memorable meal.",
                "A satisfying dish that's perfect for any occasion, featuring wholesome ingredients and bold flavors."
            ]
        
        return random.choice(descriptions)

    def generate_cooking_tips(self, cuisine, cooking_methods, ingredients):
        """Generate helpful cooking tips"""
        tips = ["Taste and adjust seasoning as you cook for the best results"]
        
        if cuisine == 'Indian':
            tips.extend([
                "Toast whole spices before grinding for deeper flavor",
                "Let curry simmer on low heat to develop rich flavors"
            ])
        elif cuisine == 'Italian':
            tips.extend([
                "Use fresh herbs when possible for the best flavor",
                "Don't overcook pasta - al dente is perfect"
            ])
        elif cuisine == 'Chinese':
            tips.extend([
                "Have all ingredients prepped before you start cooking",
                "Keep the heat high for proper stir-frying"
            ])
        
        if any('garlic' in ing.lower() for ing in ingredients):
            tips.append("Don't let garlic burn - it becomes bitter")
            
        if any(method in ['fry', 'stir-fry'] for method in cooking_methods):
            tips.append("Make sure your pan is hot before adding ingredients")
        
        return tips[:3]  # Return max 3 tips

    def generate_fallback_recipe(self, cuisine_hint=None, image_class=None):
        """Generate a basic fallback recipe"""
        cuisine = cuisine_hint or 'International'
        
        if image_class and image_class != 'Unknown':
            name = image_class.replace('_', ' ').title() + " Recipe"
        else:
            name = f"{cuisine} Recipe"
        
        basic_ingredients = [
            "2 tbsp olive oil",
            "1 large onion, chopped",
            "3 cloves garlic, minced", 
            "1 lb main protein or vegetables",
            "1 can diced tomatoes",
            "Salt and pepper to taste",
            "Fresh herbs for garnish"
        ]
        
        basic_instructions = [
            "Heat olive oil in a large pan over medium heat",
            "Add chopped onion and cook until softened, about 5 minutes",
            "Add minced garlic and cook for another minute until fragrant",
            "Add your main ingredients and cook until nearly done",
            "Add tomatoes and seasonings, simmer for 10-15 minutes",
            "Taste and adjust seasoning as needed",
            "Garnish with fresh herbs and serve hot"
        ]
        
        return {
            'success': True,
            'analysis': {
                'name': name,
                'cuisine': cuisine,
                'difficulty': 'Medium',
                'servings': 4,
                'prep_time': "15 minutes",
                'cook_time': "25 minutes", 
                'total_time': "40 minutes",
                'description': f"A delicious {cuisine.lower()} dish made with fresh ingredients and traditional cooking methods.",
                'ingredients': basic_ingredients,
                'instructions': basic_instructions,
                'cooking_methods': ['sauté', 'simmer'],
                'tags': [cuisine.lower(), 'homemade', 'medium'],
                'tips': ["Prep all ingredients before cooking", "Cook with medium heat for even results", "Taste and adjust seasoning"]
            }
        }

    # Keep all the existing extraction methods but enhance them
    def extract_ingredients(self, text):
        """Legacy method - kept for compatibility"""
        return self.extract_ingredients_from_text(text)

    def extract_cooking_methods(self, text):
        """Extract cooking methods from recipe text"""
        methods = []
        text_lower = text.lower()
        
        all_methods = self.cooking_terms['cooking_methods'] + self.cooking_terms['preparation_methods']
        
        for method in all_methods:
            if method in text_lower:
                methods.append(method)
        
        return list(set(methods))  # Remove duplicates

    def extract_cooking_time(self, text):
        """Extract cooking time from recipe text"""
        time_patterns = [
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:seconds?|secs?)',
            r'(\d+)-(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*to\s*(\d+)\s*(?:minutes?|mins?)'
        ]
        
        times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        times.append(f"{match[0]}-{match[1]}")
                    else:
                        times.append(match[0])
                else:
                    times.append(match)
        
        return times
    
    def extract_servings(self, text):
        """Extract serving information from recipe text"""
        serving_patterns = [
            r'(?:serves?|servings?)\s*:?\s*(\d+)',
            r'(\d+)\s*(?:servings?|portions?)',
            r'(?:makes?|yields?)\s*:?\s*(\d+)'
        ]
        
        for pattern in serving_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 4  # Default serving size
    
    def detect_cuisine(self, text):
        """Detect cuisine type from recipe text"""
        text_lower = text.lower()
        cuisine_scores = {}
        
        for cuisine, keywords in self.cuisine_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 1
            cuisine_scores[cuisine] = score
        
        # Return cuisine with highest score
        if cuisine_scores:
            best_cuisine = max(cuisine_scores.items(), key=lambda x: x[1])
            if best_cuisine[1] > 0:
                return best_cuisine[0]
        
        return 'International'
    
    def extract_quantity_for_ingredient(self, text, ingredient):
        """Extract quantity for a specific ingredient"""
        # Pattern to match quantities before ingredient names
        patterns = [
            rf'(\d+(?:\.\d+)?)\s*(?:' + '|'.join(self.cooking_terms['measurements']) + rf')\s*(?:of\s+)?{re.escape(ingredient)}',
            rf'(\d+(?:\.\d+)?)\s*{re.escape(ingredient)}',
            rf'(\d+(?:/\d+)?)\s*(?:' + '|'.join(self.cooking_terms['measurements']) + rf')\s*(?:of\s+)?{re.escape(ingredient)}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower(), re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "to taste"
    
    def calculate_difficulty(self, ingredients, methods, instructions):
        """Calculate recipe difficulty based on complexity"""
        difficulty_score = 0
        
        # Base score on number of ingredients
        if len(ingredients) > 15:
            difficulty_score += 3
        elif len(ingredients) > 10:
            difficulty_score += 2
        elif len(ingredients) > 5:
            difficulty_score += 1
        
        # Add score for complex cooking methods
        complex_methods = ['braise', 'confit', 'flambé', 'tempura', 'roux']
        for method in methods:
            if method in complex_methods:
                difficulty_score += 2
        
        # Add score for number of instructions
        if len(instructions) > 10:
            difficulty_score += 2
        elif len(instructions) > 7:
            difficulty_score += 1
        
        # Determine difficulty level
        if difficulty_score <= 2:
            return 'Easy'
        elif difficulty_score <= 5:
            return 'Medium'
        else:
            return 'Hard'

    def analyze_recipe_text(self, text):
        """Complete analysis of recipe text - enhanced version"""
        try:
            if not text or len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Text too short or empty'
                }
            
            # Use the new complete recipe generation
            result = self.generate_complete_recipe(text)
            
            if result['success']:
                # Return in the expected format
                return {
                    'success': True,
                    'analysis': result['analysis'],
                    'error': None
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error analyzing recipe text: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Example usage
if __name__ == "__main__":
    text_model = TextModel()
    
    # Test with ingredient list
    sample_text = """
    I want to make chicken curry with:
    - 2 lbs chicken breast
    - 1 onion
    - 3 cloves garlic
    - 1 inch ginger
    - tomatoes
    - coconut milk
    - curry powder
    - turmeric
    - cumin
    - cilantro
    
    Please help me make this into a recipe
    """
    
    result = text_model.analyze_recipe_text(sample_text)
    print(json.dumps(result, indent=2))