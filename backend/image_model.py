#!/usr/bin/env python3
"""
FlavorCraft Image Classification Model - FIXED VERSION
Properly loads dataset and classifies food images
"""

import tensorflow as tf
import numpy as np
from PIL import Image
import io
import logging
import os
import glob
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageModel:
    def __init__(self):
        """Initialize the image classification model with fixed dataset loading"""
        self.model = None
        self.label_encoder = None
        
        # Try multiple dataset paths (FIXED)
        possible_paths = [
            "data/archive (14)/images",
            "../data/archive (14)/images",
            "./data/archive (14)/images",
            "data/archive/images",
            "../data/archive/images"
        ]
        
        self.dataset_path = None
        
        # Find the correct dataset path
        for path in possible_paths:
            if Path(path).exists():
                self.dataset_path = path
                logger.info(f"✅ Dataset found at: {path}")
                break
        
        if not self.dataset_path:
            logger.warning("⚠️ No dataset found - using fallback")
            self.dataset_path = "data/archive (14)/images"
        
        # Load food categories from dataset
        self.food_categories = self.load_food_categories_from_dataset()
        self.cuisine_mapping = self.load_cuisine_mapping()
        
        # Load the classification model
        self.load_model()
        
        logger.info("✅ ImageModel initialization complete")
    
    def load_food_categories_from_dataset(self):
        """FIXED: Load food categories from actual dataset directory structure"""
        try:
            dataset_path = Path(self.dataset_path)
            logger.info(f"🔍 Scanning dataset path: {dataset_path.absolute()}")
            
            if not dataset_path.exists():
                logger.warning(f"⚠️ Dataset path {self.dataset_path} not found. Using fallback.")
                return self.get_fallback_categories()
            
            # Get all subdirectories (food classes) from the dataset
            food_folders = []
            for item in dataset_path.iterdir():
                if item.is_dir():
                    food_folders.append(item.name)
            
            if not food_folders:
                logger.warning("⚠️ No food categories found in dataset. Using fallback.")
                return self.get_fallback_categories()
            
            # Log found categories
            logger.info(f"✅ Found {len(food_folders)} food categories in dataset")
            logger.info(f"📋 Sample categories: {food_folders[:10]}")
            
            # Create food to cuisine mapping for dataset categories
            food_to_cuisine = {}
            for food in food_folders:
                cuisine = self.predict_cuisine_from_name(food)
                food_to_cuisine[food.lower()] = cuisine
            
            logger.info(f"✅ Created cuisine mapping for {len(food_to_cuisine)} foods")
            return food_to_cuisine
            
        except Exception as e:
            logger.error(f"❌ Error loading dataset categories: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return self.get_fallback_categories()
    
    def get_fallback_categories(self):
        """Fallback food categories if dataset is not available"""
        logger.info("Using fallback food categories")
        return {
            # Common international foods
            'pizza': 'Italian',
            'burger': 'American', 
            'pasta': 'Italian',
            'sushi': 'Japanese',
            'taco': 'Mexican',
            'curry': 'Indian',
            'ramen': 'Japanese',
            'salad': 'International',
            'sandwich': 'American',
            'soup': 'International',
            'rice': 'Asian',
            'bread': 'International',
            'steak': 'American',
            'chicken': 'International',
            'fish': 'International',
            'vegetables': 'International',
            'noodles': 'Asian',
            'dumplings': 'Chinese',
            'biryani': 'Indian',
            'paella': 'Spanish'
        }
    
    def predict_cuisine_from_name(self, food_name):
        """FIXED: Predict cuisine based on food name patterns"""
        food_lower = food_name.lower().replace('_', ' ')
        
        # Indian cuisine patterns
        indian_keywords = [
            'curry', 'biryani', 'tandoori', 'masala', 'dal', 'naan',
            'samosa', 'dosa', 'tikka', 'chapati', 'paratha', 'roti',
            'paneer', 'korma', 'vindaloo', 'idli', 'vada'
        ]
        
        # Italian cuisine patterns
        italian_keywords = [
            'pizza', 'pasta', 'spaghetti', 'lasagna', 'risotto',
            'carbonara', 'bruschetta', 'tiramisu', 'gelato', 'gnocchi',
            'ravioli', 'penne', 'fettuccine', 'marinara'
        ]
        
        # Chinese cuisine patterns
        chinese_keywords = [
            'dumpling', 'fried rice', 'noodles', 'spring roll', 'wonton',
            'chow mein', 'dim sum', 'peking', 'szechuan', 'kung pao',
            'sweet sour', 'lo mein', 'egg roll'
        ]
        
        # Japanese cuisine patterns
        japanese_keywords = [
            'sushi', 'ramen', 'tempura', 'miso', 'sashimi', 'teriyaki',
            'bento', 'udon', 'mochi', 'yakitori', 'tonkatsu', 'katsu'
        ]
        
        # Mexican cuisine patterns
        mexican_keywords = [
            'taco', 'burrito', 'quesadilla', 'guacamole', 'enchilada',
            'nachos', 'salsa', 'tamales', 'fajitas', 'churros'
        ]
        
        # American cuisine patterns
        american_keywords = [
            'burger', 'hot dog', 'barbecue', 'mac cheese', 'fried chicken',
            'apple pie', 'pancake', 'donut', 'steak', 'wings'
        ]
        
        # French cuisine patterns
        french_keywords = [
            'croissant', 'baguette', 'crepe', 'souffle', 'quiche',
            'ratatouille', 'bouillabaisse', 'coq vin', 'foie gras'
        ]
        
        # Check patterns
        cuisine_patterns = {
            'Indian': indian_keywords,
            'Italian': italian_keywords,
            'Chinese': chinese_keywords,
            'Japanese': japanese_keywords,
            'Mexican': mexican_keywords,
            'American': american_keywords,
            'French': french_keywords
        }
        
        for cuisine, keywords in cuisine_patterns.items():
            if any(keyword in food_lower for keyword in keywords):
                return cuisine
        
        # Default to International
        return 'International'
    
    def load_cuisine_mapping(self):
        """Load detailed cuisine information"""
        return {
            'Indian': {
                'characteristics': ['Spicy', 'Aromatic spices', 'Complex flavors', 'Rice/bread based']
            },
            'Italian': {
                'characteristics': ['Fresh ingredients', 'Tomato-based', 'Herbs', 'Pasta/pizza']
            },
            'Chinese': {
                'characteristics': ['Wok cooking', 'Balance of flavors', 'Rice/noodles', 'Stir-fry']
            },
            'Japanese': {
                'characteristics': ['Fresh ingredients', 'Minimal processing', 'Rice-based', 'Clean flavors']
            },
            'Mexican': {
                'characteristics': ['Spicy', 'Fresh herbs', 'Bold flavors', 'Corn/beans']
            },
            'American': {
                'characteristics': ['Hearty portions', 'Comfort food', 'Grilled/fried', 'Rich flavors']
            },
            'French': {
                'characteristics': ['Rich sauces', 'Butter/cream', 'Wine cooking', 'Refined techniques']
            },
            'International': {
                'characteristics': ['Diverse flavors', 'Varied techniques', 'Fusion styles']
            }
        }
    
    def load_model(self):
        """FIXED: Load pre-trained image classification model"""
        try:
            logger.info("🤖 Loading image classification model...")
            
            # Try to load custom trained model if available
            custom_model_paths = [
                'models/food_classifier.h5',
                '../models/food_classifier.h5',
                './models/food_classifier.h5',
                'backend/models/food_classifier.h5'
            ]
            
            for model_path in custom_model_paths:
                if os.path.exists(model_path):
                    try:
                        logger.info(f"Loading custom model from {model_path}...")
                        self.model = tf.keras.models.load_model(model_path)
                        logger.info("✅ Custom food classifier loaded successfully")
                        return
                    except Exception as e:
                        logger.warning(f"Failed to load custom model: {e}")
                        continue
            
            # Fallback to pre-trained ResNet50 model
            logger.info("Loading pre-trained ResNet50 model...")
            from tensorflow.keras.applications import ResNet50
            from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
            
            self.model = ResNet50(weights='imagenet')
            self.preprocess_input = preprocess_input
            self.decode_predictions = decode_predictions
            logger.info("✅ ResNet50 model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.model = None
    
    def preprocess_image(self, image_file):
        """FIXED: Preprocess image for model prediction"""
        try:
            logger.info("📸 Preprocessing image...")
            
            # Handle different input types
            if isinstance(image_file, str):
                # File path
                img = Image.open(image_file)
                logger.info(f"📸 Loaded from file path: {image_file}")
            else:
                # File object - handle properly
                if hasattr(image_file, 'seek'):
                    image_file.seek(0)  # Reset to beginning
                
                if hasattr(image_file, 'read'):
                    # Read the file content
                    image_data = image_file.read()
                    img = Image.open(io.BytesIO(image_data))
                    logger.info(f"📸 Loaded from file object, size: {len(image_data)} bytes")
                else:
                    img = Image.open(image_file)
            
            logger.info(f"📸 Original image: {img.size}, mode: {img.mode}")
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logger.info("📸 Converted to RGB")
            
            # Resize to model input size (224x224 for ResNet50)
            img = img.resize((224, 224))
            logger.info("📸 Resized to 224x224")
            
            # Convert to array
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            
            # Apply preprocessing based on model type
            if hasattr(self, 'preprocess_input'):
                # ResNet50 preprocessing
                img_array = self.preprocess_input(img_array)
                logger.info("📸 Applied ResNet50 preprocessing")
            else:
                # Standard normalization
                img_array = img_array / 255.0
                logger.info("📸 Applied standard normalization")
            
            logger.info(f"✅ Image preprocessing completed. Shape: {img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing image: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def analyze_image_for_recipe(self, image_file):
        """FIXED: Complete image analysis pipeline for recipe generation"""
        try:
            logger.info("🚀 Starting image analysis...")
            
            if self.model is None:
                logger.error("❌ No model available for classification")
                return {
                    'success': False,
                    'predictions': [],
                    'food_class': 'Unknown',
                    'cuisine': 'Unknown',
                    'confidence': 0.0,
                    'error': 'Image classification model not loaded'
                }
            
            # Preprocess the image
            processed_image = self.preprocess_image(image_file)
            if processed_image is None:
                logger.error("❌ Image preprocessing failed")
                return {
                    'success': False,
                    'predictions': [],
                    'food_class': 'Unknown',
                    'cuisine': 'Unknown',
                    'confidence': 0.0,
                    'error': 'Image preprocessing failed'
                }
            
            # Make prediction
            logger.info("🔮 Making prediction...")
            predictions = self.model.predict(processed_image, verbose=0)
            logger.info(f"✅ Prediction completed: shape {predictions.shape}")
            
            # Process predictions based on model type
            if hasattr(self, 'decode_predictions'):
                # Using ImageNet ResNet50
                decoded_predictions = self.decode_predictions(predictions, top=5)[0]
                
                # Process predictions to find food-related items
                food_predictions = []
                for pred in decoded_predictions:
                    class_id = pred[0]
                    class_name = pred[1].lower()
                    confidence = float(pred[2])
                    
                    food_predictions.append({
                        'class_id': class_id,
                        'class': class_name,
                        'confidence': confidence,
                        'description': pred[1]
                    })
                
                # Get best prediction
                best_prediction = food_predictions[0]
                best_class = best_prediction['class']
                
                # Try to map to known food categories
                mapped_food = self.map_imagenet_to_food(best_class)
                
                # Determine cuisine
                cuisine = self.determine_cuisine_from_prediction(mapped_food)
                
                logger.info(f"✅ Best prediction: {mapped_food} (confidence: {best_prediction['confidence']:.3f})")
                logger.info(f"🌍 Determined cuisine: {cuisine}")
                
                return {
                    'success': True,
                    'predictions': food_predictions,
                    'food_class': mapped_food,
                    'cuisine': cuisine,
                    'confidence': best_prediction['confidence'],
                    'model_used': 'ResNet50-ImageNet',
                    'raw_prediction': best_prediction['description'],
                    'error': None
                }
            
            else:
                # Custom model prediction logic
                logger.warning("⚠️ Custom model prediction not fully implemented")
                
                # Get class with highest confidence
                predicted_class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class_idx])
                
                # Map to food categories if possible
                food_categories_list = list(self.food_categories.keys())
                if predicted_class_idx < len(food_categories_list):
                    predicted_food = food_categories_list[predicted_class_idx]
                    cuisine = self.food_categories.get(predicted_food, 'International')
                else:
                    predicted_food = 'Unknown'
                    cuisine = 'International'
                
                logger.info(f"✅ Custom model prediction: {predicted_food} (confidence: {confidence:.3f})")
                
                return {
                    'success': True,
                    'predictions': [{'class': predicted_food, 'confidence': confidence}],
                    'food_class': predicted_food,
                    'cuisine': cuisine,
                    'confidence': confidence,
                    'model_used': 'Custom-Food-Classifier',
                    'error': None
                }
            
        except Exception as e:
            logger.error(f"❌ Error in image analysis: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'predictions': [],
                'food_class': 'Unknown',
                'cuisine': 'Unknown',
                'confidence': 0.0,
                'error': f'Image analysis failed: {str(e)}'
            }
    
    def map_imagenet_to_food(self, imagenet_class):
        """FIXED: Map ImageNet predictions to our food categories"""
        
        # Create mapping from ImageNet classes to food names
        imagenet_food_mapping = {
            # Bread and baked goods
            'bagel': 'bagel',
            'pretzel': 'pretzel',
            'croissant': 'croissant',
            'muffin': 'muffin',
            'dough': 'bread',
            
            # Pizza and Italian
            'pizza': 'pizza',
            'spaghetti_squash': 'pasta',
            'carbonara': 'pasta',
            
            # Asian foods
            'dumpling': 'dumplings',
            'wonton': 'dumplings',
            'chow_mein': 'noodles',
            'ramen': 'ramen',
            'sushi': 'sushi',
            
            # American foods
            'cheeseburger': 'burger',
            'hamburger': 'burger',
            'hotdog': 'hot_dog',
            'french_loaf': 'sandwich',
            
            # Desserts
            'ice_cream': 'ice_cream',
            'chocolate_sauce': 'chocolate',
            'custard': 'custard',
            'pudding': 'pudding',
            
            # Meat dishes
            'meatloaf': 'meatloaf',
            'pot_pie': 'pot_pie',
            'consomme': 'soup',
            
            # Fruits and vegetables
            'bell_pepper': 'vegetables',
            'broccoli': 'vegetables',
            'cauliflower': 'vegetables',
            'cucumber': 'vegetables',
            'mushroom': 'vegetables',
            
            # Generic mappings
            'plate': 'mixed_dish',
            'platter': 'mixed_dish',
            'tray': 'mixed_dish'
        }
        
        # Check for direct mapping
        for imagenet_key, food_name in imagenet_food_mapping.items():
            if imagenet_key in imagenet_class.lower():
                logger.info(f"🎯 Mapped '{imagenet_class}' to '{food_name}'")
                return food_name
        
        # Check if it matches any of our dataset categories
        for food_category in self.food_categories.keys():
            if food_category in imagenet_class.lower() or imagenet_class.lower() in food_category:
                logger.info(f"🎯 Direct match: '{imagenet_class}' -> '{food_category}'")
                return food_category
        
        # Fallback: use the ImageNet class name directly (cleaned up)
        cleaned_class = imagenet_class.replace('_', ' ').title()
        logger.info(f"🎯 Using cleaned ImageNet class: '{cleaned_class}'")
        return cleaned_class
    
    def determine_cuisine_from_prediction(self, food_name):
        """FIXED: Determine cuisine from predicted food name"""
        
        # Check if we have this food in our categories
        food_lower = food_name.lower()
        
        if food_lower in self.food_categories:
            cuisine = self.food_categories[food_lower]
            logger.info(f"🌍 Found cuisine in categories: {food_name} -> {cuisine}")
            return cuisine
        
        # Use the cuisine prediction logic
        cuisine = self.predict_cuisine_from_name(food_name)
        logger.info(f"🌍 Predicted cuisine from name: {food_name} -> {cuisine}")
        return cuisine

# Test function for standalone usage
if __name__ == "__main__":
    logger.info("🧪 Testing ImageModel...")
    
    try:
        model = ImageModel()
        logger.info("✅ ImageModel initialized successfully")
        
        # Log model info
        if hasattr(model, 'food_categories'):
            logger.info(f"📊 Food categories loaded: {len(model.food_categories)}")
            sample_categories = list(model.food_categories.keys())[:5]
            logger.info(f"📋 Sample categories: {sample_categories}")
        
        logger.info("🧪 ImageModel test completed")
        
    except Exception as e:
        logger.error(f"❌ ImageModel test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())