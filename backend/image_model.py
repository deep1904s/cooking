#!/usr/bin/env python3
"""
FlavorCraft Image Classification Model - UPDATED VERSION
Properly loads custom trained H5 model and PKL files for food classification
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
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageModel:
    def __init__(self):
        """Initialize the image classification model with custom H5 model and PKL files"""
        self.model = None
        self.label_map = None
        self.class_names = None
        self.label_encoder = None
        
        # Try multiple dataset paths (FIXED for cooking project structure)
        possible_paths = [
            "data/data1/images",           # From root directory
            "../data/data1/images",        # From backend directory
            "../../data/data1/images",     # From backend/models directory
            "./data/data1/images",         # Current directory
            "../../../data/data1/images"   # Deep nested fallback
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
        
        # Load the custom trained model and label mappings
        self.load_custom_model()
        
        # Load food categories and cuisine mapping
        self.food_categories = self.load_food_categories_from_dataset()
        self.cuisine_mapping = self.load_cuisine_mapping()
        
        logger.info("✅ ImageModel initialization complete")
    
    def load_custom_model(self):
        """Load custom trained H5 model and PKL files"""
        try:
            logger.info("🤖 Loading custom trained food classification model...")
            
            # Model and label map paths (updated for cooking project structure)
            model_paths = [
                'models/food_classifier.h5',           # From root directory
                '../models/food_classifier.h5',        # From backend directory  
                '../../models/food_classifier.h5',     # From backend/models directory
                './models/food_classifier.h5',         # Current directory
                '../../../models/food_classifier.h5'   # Deep nested fallback
            ]
            
            label_map_paths = [
                'models/label_map.pkl',                 # From root directory
                '../models/label_map.pkl',              # From backend directory
                '../../models/label_map.pkl',           # From backend/models directory  
                './models/label_map.pkl',               # Current directory
                '../../../models/label_map.pkl'        # Deep nested fallback
            ]
            
            # Try to load custom model
            model_loaded = False
            for model_path in model_paths:
                if os.path.exists(model_path):
                    try:
                        logger.info(f"Loading custom H5 model from {model_path}...")
                        self.model = tf.keras.models.load_model(model_path)
                        logger.info("✅ Custom H5 model loaded successfully!")
                        model_loaded = True
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load H5 model from {model_path}: {e}")
                        continue
            
            # Try to load label map
            label_map_loaded = False
            for label_path in label_map_paths:
                if os.path.exists(label_path):
                    try:
                        logger.info(f"Loading label map from {label_path}...")
                        with open(label_path, 'rb') as f:
                            self.label_map = pickle.load(f)
                        
                        # Create reverse mapping (index -> class name)
                        self.class_names = {v: k for k, v in self.label_map.items()}
                        logger.info(f"✅ Label map loaded with {len(self.label_map)} classes")
                        logger.info(f"📋 Sample classes: {list(self.label_map.keys())[:5]}")
                        label_map_loaded = True
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load label map from {label_path}: {e}")
                        continue
            
            if model_loaded and label_map_loaded:
                logger.info("✅ Custom model and label map loaded successfully!")
                return
            elif model_loaded and not label_map_loaded:
                logger.warning("⚠️ Model loaded but no label map found. Creating fallback mapping.")
                self.create_fallback_label_map()
                return
            else:
                logger.warning("⚠️ Custom model not found, falling back to pre-trained model...")
                self.load_pretrained_model()
                
        except Exception as e:
            logger.error(f"❌ Error loading custom model: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.load_pretrained_model()
    
    def create_fallback_label_map(self):
        """Create fallback label mapping when PKL file is not available"""
        try:
            if self.dataset_path and Path(self.dataset_path).exists():
                dataset_path = Path(self.dataset_path)
                food_folders = []
                for item in dataset_path.iterdir():
                    if item.is_dir():
                        food_folders.append(item.name)
                
                food_folders.sort()  # Ensure consistent ordering
                self.label_map = {name: idx for idx, name in enumerate(food_folders)}
                self.class_names = {idx: name for idx, name in enumerate(food_folders)}
                logger.info(f"✅ Created fallback label map with {len(self.label_map)} classes")
            else:
                # Ultimate fallback with common food categories
                fallback_classes = [
                    'burger', 'pizza', 'pasta', 'sushi', 'taco', 'curry', 'salad',
                    'sandwich', 'soup', 'rice', 'noodles', 'chicken', 'fish'
                ]
                self.label_map = {name: idx for idx, name in enumerate(fallback_classes)}
                self.class_names = {idx: name for idx, name in enumerate(fallback_classes)}
                logger.info("✅ Created ultimate fallback label map")
                
        except Exception as e:
            logger.error(f"❌ Error creating fallback label map: {e}")
            self.label_map = {}
            self.class_names = {}
    
    def load_pretrained_model(self):
        """Fallback to pre-trained ResNet50 model"""
        try:
            logger.info("Loading pre-trained ResNet50 model as fallback...")
            from tensorflow.keras.applications import ResNet50
            from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
            
            self.model = ResNet50(weights='imagenet')
            self.preprocess_input = preprocess_input
            self.decode_predictions = decode_predictions
            self.use_imagenet = True
            logger.info("✅ ResNet50 fallback model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Error loading fallback model: {str(e)}")
            self.model = None
    
    def load_food_categories_from_dataset(self):
        """Load food categories from actual dataset directory structure"""
        try:
            # If we have a custom label map, use it
            if self.label_map:
                food_to_cuisine = {}
                for food_name in self.label_map.keys():
                    cuisine = self.predict_cuisine_from_name(food_name)
                    food_to_cuisine[food_name.lower()] = cuisine
                
                logger.info(f"✅ Created cuisine mapping from custom label map: {len(food_to_cuisine)} foods")
                return food_to_cuisine
            
            # Otherwise, scan dataset directory
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
            
            # Create food to cuisine mapping for dataset categories
            food_to_cuisine = {}
            for food in food_folders:
                cuisine = self.predict_cuisine_from_name(food)
                food_to_cuisine[food.lower()] = cuisine
            
            logger.info(f"✅ Created cuisine mapping for {len(food_to_cuisine)} foods")
            return food_to_cuisine
            
        except Exception as e:
            logger.error(f"❌ Error loading dataset categories: {str(e)}")
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
        """Predict cuisine based on food name patterns"""
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
    
    def preprocess_image(self, image_file):
        """Preprocess image for model prediction (optimized for custom MobileNetV2 model)"""
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
            
            # Resize to model input size (224x224 for MobileNetV2/ResNet50)
            img = img.resize((224, 224))
            logger.info("📸 Resized to 224x224")
            
            # Convert to array
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            
            # Apply preprocessing based on model type
            if hasattr(self, 'use_imagenet') and self.use_imagenet:
                # ResNet50 preprocessing
                img_array = self.preprocess_input(img_array)
                logger.info("📸 Applied ResNet50 preprocessing")
            else:
                # Custom model preprocessing (same as training: rescale 1./255)
                img_array = img_array / 255.0
                logger.info("📸 Applied custom model preprocessing (rescale 1./255)")
            
            logger.info(f"✅ Image preprocessing completed. Shape: {img_array.shape}")
            return img_array
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing image: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def analyze_image_for_recipe(self, image_file):
        """Complete image analysis pipeline for recipe generation using custom trained model"""
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
            if hasattr(self, 'use_imagenet') and self.use_imagenet:
                # Using ImageNet ResNet50 (fallback)
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
                
                # Get best prediction and map it
                best_prediction = food_predictions[0]
                best_class = best_prediction['class']
                mapped_food = self.map_imagenet_to_food(best_class)
                cuisine = self.determine_cuisine_from_prediction(mapped_food)
                
                logger.info(f"✅ ImageNet prediction: {mapped_food} (confidence: {best_prediction['confidence']:.3f})")
                
                return {
                    'success': True,
                    'predictions': food_predictions,
                    'food_class': mapped_food,
                    'cuisine': cuisine,
                    'confidence': best_prediction['confidence'],
                    'model_used': 'ResNet50-ImageNet-Fallback',
                    'raw_prediction': best_prediction['description'],
                    'error': None
                }
            
            else:
                # Custom trained model prediction
                logger.info("🎯 Using custom trained food classifier...")
                
                # Get top predictions
                top_indices = np.argsort(predictions[0])[::-1][:5]  # Top 5 predictions
                food_predictions = []
                
                for i, idx in enumerate(top_indices):
                    confidence = float(predictions[0][idx])
                    
                    # Get class name from label map
                    if self.class_names and idx in self.class_names:
                        class_name = self.class_names[idx]
                    else:
                        class_name = f"class_{idx}"
                    
                    food_predictions.append({
                        'class_id': int(idx),
                        'class': class_name,
                        'confidence': confidence,
                        'description': class_name.replace('_', ' ').title()
                    })
                    
                    if i == 0:  # Log best prediction
                        logger.info(f"🎯 Best prediction: {class_name} (confidence: {confidence:.3f})")
                
                # Get best prediction details
                best_prediction = food_predictions[0]
                predicted_food = best_prediction['class']
                
                # Determine cuisine
                cuisine = self.determine_cuisine_from_prediction(predicted_food)
                
                logger.info(f"✅ Custom model prediction: {predicted_food}")
                logger.info(f"🌍 Determined cuisine: {cuisine}")
                
                return {
                    'success': True,
                    'predictions': food_predictions,
                    'food_class': predicted_food,
                    'cuisine': cuisine,
                    'confidence': best_prediction['confidence'],
                    'model_used': 'Custom-MobileNetV2-Food-Classifier',
                    'raw_prediction': best_prediction['description'],
                    'total_classes': len(self.class_names) if self.class_names else 'Unknown',
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
        """Map ImageNet predictions to our food categories (for fallback model)"""
        
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
        """Determine cuisine from predicted food name"""
        
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
    
    def get_model_info(self):
        """Get information about the loaded model"""
        info = {
            'model_loaded': self.model is not None,
            'model_type': 'Unknown',
            'total_classes': 0,
            'sample_classes': [],
            'has_label_map': self.label_map is not None
        }
        
        if hasattr(self, 'use_imagenet') and self.use_imagenet:
            info['model_type'] = 'ResNet50-ImageNet-Fallback'
            info['total_classes'] = 1000
        elif self.class_names:
            info['model_type'] = 'Custom-MobileNetV2-Food-Classifier'
            info['total_classes'] = len(self.class_names)
            info['sample_classes'] = list(self.class_names.values())[:10]
        
        return info

# Test function for standalone usage
if __name__ == "__main__":
    logger.info("🧪 Testing ImageModel...")
    
    try:
        model = ImageModel()
        logger.info("✅ ImageModel initialized successfully")
        
        # Log model info
        model_info = model.get_model_info()
        logger.info(f"📊 Model Info: {model_info}")
        
        if hasattr(model, 'food_categories'):
            logger.info(f"📊 Food categories loaded: {len(model.food_categories)}")
            sample_categories = list(model.food_categories.keys())[:5]
            logger.info(f"📋 Sample categories: {sample_categories}")
        
        logger.info("🧪 ImageModel test completed")
        
    except Exception as e:
        logger.error(f"❌ ImageModel test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())