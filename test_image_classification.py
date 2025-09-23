#!/usr/bin/env python3
"""
Debug Image Classification Test
Test your image classification separately
"""

import os
import sys
from pathlib import Path

def test_dataset_path():
    """Test if dataset can be found"""
    print("🔍 Testing Dataset Path...")
    
    # Test the exact path you mentioned
    dataset_paths = [
        "data/archive (14)/images",
        "data/archive/images", 
        "../data/archive (14)/images",
        "./data/archive (14)/images"
    ]
    
    for path in dataset_paths:
        dataset_path = Path(path)
        print(f"\n📂 Testing path: {dataset_path.absolute()}")
        
        if dataset_path.exists():
            print(f"✅ Found: {path}")
            
            # List food categories
            food_folders = [f.name for f in dataset_path.iterdir() if f.is_dir()]
            print(f"📊 Food categories found: {len(food_folders)}")
            print(f"📋 Sample categories: {food_folders[:5]}")
            
            # Test one category
            if food_folders:
                test_category = food_folders[0]
                test_path = dataset_path / test_category
                images = list(test_path.glob('*.jpg')) + list(test_path.glob('*.png')) + list(test_path.glob('*.jpeg'))
                print(f"🖼️  Images in '{test_category}': {len(images)}")
            
            return True
        else:
            print(f"❌ Not found: {path}")
    
    print("\n❌ No dataset found at any location!")
    return False

def test_image_model():
    """Test image model loading"""
    print("\n🤖 Testing Image Model...")
    
    try:
        # Add current directory to Python path
        sys.path.append('.')
        sys.path.append('./backend')
        
        from image_model import ImageModel
        print("✅ Image model imported successfully")
        
        # Initialize model
        model = ImageModel()
        print("✅ Image model initialized")
        
        # Check dataset path in model
        print(f"📂 Model dataset path: {model.dataset_path}")
        
        # Check food categories loaded
        print(f"🍽️  Food categories loaded: {len(model.food_categories)}")
        if model.food_categories:
            sample_foods = list(model.food_categories.keys())[:5]
            print(f"📋 Sample foods: {sample_foods}")
        
        return model
        
    except Exception as e:
        print(f"❌ Image model error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_image_classification(model, test_image_path=None):
    """Test image classification with a sample image"""
    if not model:
        print("❌ No model available for testing")
        return
    
    print(f"\n📸 Testing Image Classification...")
    
    if test_image_path and Path(test_image_path).exists():
        print(f"🖼️  Testing with: {test_image_path}")
        
        try:
            # Test classification
            result = model.analyze_image_for_recipe(test_image_path)
            print(f"📊 Classification result: {result}")
            
            if result.get('success'):
                print(f"✅ Classified as: {result.get('food_class')}")
                print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
                print(f"🌍 Cuisine: {result.get('cuisine')}")
            else:
                print(f"❌ Classification failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Classification error: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠️  No test image provided or image not found")

def main():
    print("🍕" * 20)
    print("🔍 FLAVORCRAFT IMAGE DEBUG")
    print("🍕" * 20)
    
    # Test dataset
    dataset_found = test_dataset_path()
    
    # Test model
    model = test_image_model()
    
    # Test with sample image (if available)
    # You can provide a path to test image here
    test_image_path = "data/archive (14)/images/baklava/50627.jpg"
    test_image_classification(model, test_image_path)
    
    print("\n" + "="*40)
    print("🎯 DEBUG SUMMARY")
    print("="*40)
    print(f"📊 Dataset Found: {'✅' if dataset_found else '❌'}")
    print(f"🤖 Model Loaded: {'✅' if model else '❌'}")
    
    if not dataset_found:
        print("\n💡 SOLUTION: Fix dataset path")
        print("   1. Check if data/archive (14)/images/ exists")
        print("   2. Update image_model.py dataset_path")
    
    if not model:
        print("\n💡 SOLUTION: Fix model loading")
        print("   1. Check image_model.py imports")
        print("   2. Install missing dependencies")

if __name__ == "__main__":
    main()
