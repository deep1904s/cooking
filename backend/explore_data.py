#!/usr/bin/env python3
"""
FlavorCraft Dataset Explorer
Explore and analyze the food dataset in data/archive/images/
"""

import os
import json
from pathlib import Path
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def explore_food_dataset():
    """Explore the food dataset and generate statistics"""
    dataset_path = Path("data/archive/images")
    
    print("🍕" * 20)
    print("🔍 FLAVORCRAFT DATASET EXPLORER")
    print("🍕" * 20)
    
    if not dataset_path.exists():
        print(f"❌ Dataset not found at: {dataset_path}")
        print("📝 Please ensure your dataset is placed in: data/archive/images/")
        print("📁 Expected structure: data/archive/images/[food_category]/[image_files]")
        return
    
    print(f"📂 Dataset path: {dataset_path}")
    
    # Get all food categories (directories)
    food_categories = []
    total_images = 0
    category_stats = {}
    
    for item in dataset_path.iterdir():
        if item.is_dir():
            food_categories.append(item.name)
            
            # Count images in this category
            image_files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']:
                image_files.extend(list(item.glob(ext)))
                image_files.extend(list(item.glob(ext.upper())))
            
            num_images = len(image_files)
            category_stats[item.name] = num_images
            total_images += num_images
    
    # Sort categories
    food_categories.sort()
    
    print(f"📊 Dataset Statistics:")
    print(f"   🏷️  Total food categories: {len(food_categories)}")
    print(f"   🖼️  Total images: {total_images:,}")
    print(f"   📈 Average images per category: {total_images//len(food_categories) if food_categories else 0}")
    
    # Show top 10 categories by image count
    top_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    
    print(f"\n🔝 Top 10 Categories by Image Count:")
    for i, (category, count) in enumerate(top_categories, 1):
        print(f"   {i:2d}. {category:25} - {count:4d} images")
    
    # Show sample categories
    print(f"\n📋 Sample Food Categories:")
    sample_categories = food_categories[:15] if len(food_categories) > 15 else food_categories
    for i, category in enumerate(sample_categories, 1):
        print(f"   {i:2d}. {category}")
    
    if len(food_categories) > 15:
        print(f"   ... and {len(food_categories) - 15} more categories")
    
    # Generate cuisine mapping
    print(f"\n🌍 Generating Cuisine Mapping...")
    cuisine_mapping = generate_cuisine_mapping(food_categories)
    
    cuisine_stats = Counter(cuisine_mapping.values())
    print(f"📊 Cuisine Distribution:")
    for cuisine, count in cuisine_stats.most_common():
        print(f"   {cuisine:15} - {count:3d} categories")
    
    # Save dataset info
    dataset_info = {
        'total_categories': len(food_categories),
        'total_images': total_images,
        'categories': food_categories,
        'category_image_counts': category_stats,
        'cuisine_mapping': cuisine_mapping,
        'cuisine_distribution': dict(cuisine_stats),
        'dataset_path': str(dataset_path),
        'last_analyzed': str(Path.cwd())
    }
    
    # Save to JSON file
    output_file = "dataset_info.json"
    with open(output_file, 'w') as f:
        json.dump(dataset_info, f, indent=2)
    
    print(f"\n💾 Dataset information saved to: {output_file}")
    print(f"✅ Dataset exploration complete!")
    
    return dataset_info

def generate_cuisine_mapping(food_categories):
    """Generate cuisine mapping for food categories"""
    cuisine_mapping = {}
    
    for category in food_categories:
        category_lower = category.lower()
        
        # Indian cuisine patterns
        if any(keyword in category_lower for keyword in [
            'curry', 'biryani', 'tandoori', 'masala', 'dal', 'naan', 
            'samosa', 'dosa', 'tikka', 'chapati', 'paratha', 'roti',
            'vindaloo', 'korma', 'paneer', 'chai'
        ]):
            cuisine_mapping[category] = 'Indian'
        
        # Italian cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'pizza', 'pasta', 'spaghetti', 'lasagna', 'risotto', 
            'carbonara', 'bruschetta', 'tiramisu', 'gelato', 'cappuccino',
            'gnocchi', 'ravioli', 'pesto', 'minestrone'
        ]):
            cuisine_mapping[category] = 'Italian'
        
        # Chinese cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'dumpling', 'fried_rice', 'noodles', 'spring_roll', 'wonton',
            'chow_mein', 'dim_sum', 'peking', 'szechuan', 'kung_pao',
            'sweet_sour', 'lo_mein'
        ]):
            cuisine_mapping[category] = 'Chinese'
        
        # Japanese cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'sushi', 'ramen', 'tempura', 'miso', 'sashimi', 'teriyaki',
            'bento', 'udon', 'mochi', 'sake', 'edamame', 'yakitori'
        ]):
            cuisine_mapping[category] = 'Japanese'
        
        # Mexican cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'taco', 'burrito', 'quesadilla', 'guacamole', 'enchilada',
            'nachos', 'salsa', 'tamales', 'fajitas', 'churros',
            'tortilla', 'ceviche'
        ]):
            cuisine_mapping[category] = 'Mexican'
        
        # American cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'burger', 'hot_dog', 'barbecue', 'mac_and_cheese', 'fried_chicken',
            'apple_pie', 'pancake', 'donut', 'bagel', 'cheesecake',
            'coleslaw', 'cornbread'
        ]):
            cuisine_mapping[category] = 'American'
        
        # French cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'croissant', 'baguette', 'crepe', 'bouillabaisse', 'ratatouille',
            'coq_au_vin', 'souffle', 'macaron', 'escargot', 'quiche',
            'brie', 'camembert'
        ]):
            cuisine_mapping[category] = 'French'
        
        # Thai cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'pad_thai', 'green_curry', 'tom_yum', 'som_tam', 'massaman',
            'thai', 'coconut_curry'
        ]):
            cuisine_mapping[category] = 'Thai'
        
        # Mediterranean cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'hummus', 'falafel', 'pita', 'greek_salad', 'moussaka',
            'baklava', 'tzatziki', 'gyros', 'spanakopita', 'olives'
        ]):
            cuisine_mapping[category] = 'Mediterranean'
        
        # Korean cuisine patterns
        elif any(keyword in category_lower for keyword in [
            'kimchi', 'bulgogi', 'bibimbap', 'korean', 'gochujang'
        ]):
            cuisine_mapping[category] = 'Korean'
        
        # Default to International
        else:
            cuisine_mapping[category] = 'International'
    
    return cuisine_mapping

if __name__ == "__main__":
    explore_food_dataset()
