#!/usr/bin/env python3
"""
FlavorCraft Model Accuracy Evaluation Script
Evaluates your trained food classifier model performance
"""

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from pathlib import Path
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_model_accuracy():
    """Comprehensive evaluation of the trained food classifier"""
    
    # Paths
    dataset_dir = "data/data1/images"
    model_path = "models/food_classifier.h5"
    label_map_path = "models/label_map.pkl"
    history_path = "models/training_history.pkl"
    
    # Check if files exist
    if not Path(model_path).exists():
        logger.error(f"❌ Model not found: {model_path}")
        logger.error("Please train the model first using train_food_classifier.py")
        return False
    
    if not Path(dataset_dir).exists():
        logger.error(f"❌ Dataset not found: {dataset_dir}")
        return False
    
    logger.info("🚀 Starting model evaluation...")
    
    try:
        # Load the trained model
        logger.info(f"📥 Loading model from {model_path}...")
        model = tf.keras.models.load_model(model_path)
        logger.info("✅ Model loaded successfully!")
        
        # Display model architecture
        logger.info("🏗️ Model Architecture:")
        model.summary()
        
        # Load label map
        if Path(label_map_path).exists():
            logger.info(f"📥 Loading label map from {label_map_path}...")
            with open(label_map_path, 'rb') as f:
                class_indices = pickle.load(f)
            class_names = list(class_indices.keys())
            logger.info(f"✅ Found {len(class_names)} classes")
        else:
            logger.warning("⚠️ Label map not found, using numeric indices")
            class_names = None
        
        # Create test data generator
        logger.info("🔄 Creating test data generator...")
        test_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)
        
        # Use validation split as test set
        test_generator = test_datagen.flow_from_directory(
            dataset_dir,
            target_size=(224, 224),
            batch_size=32,
            class_mode='categorical',
            subset='validation',
            shuffle=False  # Important for accurate evaluation
        )
        
        logger.info(f"📊 Test samples: {test_generator.samples}")
        logger.info(f"📊 Test classes: {test_generator.num_classes}")
        
        # Evaluate on test set
        logger.info("🎯 Evaluating model on test set...")
        test_loss, test_accuracy = model.evaluate(test_generator, verbose=1)
        
        logger.info("=" * 50)
        logger.info("📈 MODEL PERFORMANCE RESULTS")
        logger.info("=" * 50)
        logger.info(f"🎯 Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        logger.info(f"📉 Test Loss: {test_loss:.4f}")
        
        # Get detailed predictions
        logger.info("🔮 Generating detailed predictions...")
        predictions = model.predict(test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        # Classification report
        if class_names:
            target_names = [class_names[i] for i in range(len(class_names))]
        else:
            target_names = [f"Class_{i}" for i in range(test_generator.num_classes)]
        
        logger.info("\n📊 DETAILED CLASSIFICATION REPORT:")
        print("\n" + "="*60)
        print("CLASSIFICATION REPORT")
        print("="*60)
        report = classification_report(true_classes, predicted_classes, 
                                     target_names=target_names, digits=4)
        print(report)
        
        # Per-class accuracy
        logger.info("\n🎯 PER-CLASS ACCURACY:")
        print("\n" + "="*40)
        print("PER-CLASS ACCURACY")
        print("="*40)
        
        class_correct = {}
        class_total = {}
        
        for i in range(len(true_classes)):
            true_class = true_classes[i]
            pred_class = predicted_classes[i]
            
            if true_class not in class_total:
                class_total[true_class] = 0
                class_correct[true_class] = 0
            
            class_total[true_class] += 1
            if true_class == pred_class:
                class_correct[true_class] += 1
        
        for class_idx in sorted(class_total.keys()):
            if class_names and class_idx < len(class_names):
                class_name = class_names[class_idx]
            else:
                class_name = f"Class_{class_idx}"
            
            accuracy = class_correct[class_idx] / class_total[class_idx]
            print(f"{class_name:20s}: {accuracy:.4f} ({accuracy*100:.2f}%) "
                  f"[{class_correct[class_idx]}/{class_total[class_idx]}]")
        
        # Top-K accuracy
        logger.info("\n🏆 TOP-K ACCURACY:")
        print("\n" + "="*30)
        print("TOP-K ACCURACY")
        print("="*30)
        
        for k in [1, 3, 5]:
            if k <= test_generator.num_classes:
                top_k_acc = tf.keras.metrics.top_k_categorical_accuracy(
                    tf.keras.utils.to_categorical(true_classes, test_generator.num_classes),
                    predictions, k=k
                )
                avg_top_k_acc = np.mean(top_k_acc)
                print(f"Top-{k} Accuracy: {avg_top_k_acc:.4f} ({avg_top_k_acc*100:.2f}%)")
        
        # Load and display training history if available
        if Path(history_path).exists():
            logger.info("\n📈 TRAINING HISTORY:")
            with open(history_path, 'rb') as f:
                history = pickle.load(f)
            
            print("\n" + "="*40)
            print("TRAINING HISTORY")
            print("="*40)
            
            final_train_acc = history['accuracy'][-1]
            final_val_acc = history['val_accuracy'][-1]
            final_train_loss = history['loss'][-1]
            final_val_loss = history['val_loss'][-1]
            
            print(f"Final Training Accuracy:   {final_train_acc:.4f} ({final_train_acc*100:.2f}%)")
            print(f"Final Validation Accuracy: {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
            print(f"Final Training Loss:       {final_train_loss:.4f}")
            print(f"Final Validation Loss:     {final_val_loss:.4f}")
            
            # Plot training history
            try:
                plot_training_history(history)
                logger.info("📊 Training plots saved as 'training_plots.png'")
            except Exception as e:
                logger.warning(f"Could not create plots: {e}")
        
        # Model size and parameters
        logger.info("\n🔧 MODEL SPECIFICATIONS:")
        print("\n" + "="*40)
        print("MODEL SPECIFICATIONS")
        print("="*40)
        
        total_params = model.count_params()
        trainable_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
        non_trainable_params = total_params - trainable_params
        
        print(f"Total Parameters:        {total_params:,}")
        print(f"Trainable Parameters:    {trainable_params:,}")
        print(f"Non-trainable Parameters: {non_trainable_params:,}")
        
        # Model file size
        model_size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"Model File Size:         {model_size_mb:.2f} MB")
        
        # Performance summary
        logger.info("\n🏆 PERFORMANCE SUMMARY:")
        print("\n" + "="*50)
        print("PERFORMANCE SUMMARY")
        print("="*50)
        
        if test_accuracy >= 0.90:
            performance_level = "🌟 EXCELLENT"
        elif test_accuracy >= 0.80:
            performance_level = "✅ GOOD"
        elif test_accuracy >= 0.70:
            performance_level = "⚠️ FAIR"
        else:
            performance_level = "❌ NEEDS IMPROVEMENT"
        
        print(f"Overall Performance: {performance_level}")
        print(f"Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
        print(f"Model Type: MobileNetV2 Transfer Learning")
        print(f"Dataset Classes: {test_generator.num_classes}")
        print(f"Test Samples: {test_generator.samples}")
        
        # Recommendations
        print("\n📋 RECOMMENDATIONS:")
        if test_accuracy < 0.70:
            print("- Consider increasing training epochs")
            print("- Add more data augmentation")
            print("- Try fine-tuning more layers")
            print("- Check data quality and labeling")
        elif test_accuracy < 0.85:
            print("- Good performance! Consider fine-tuning")
            print("- Add more training data if available")
            print("- Experiment with different architectures")
        else:
            print("- Excellent performance!")
            print("- Model is ready for production use")
            print("- Consider deployment optimization")
        
        logger.info("✅ Model evaluation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during evaluation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def plot_training_history(history):
    """Plot training history graphs"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Training History', fontsize=16)
    
    epochs = range(1, len(history['accuracy']) + 1)
    
    # Accuracy plot
    axes[0, 0].plot(epochs, history['accuracy'], 'b-', label='Training Accuracy')
    axes[0, 0].plot(epochs, history['val_accuracy'], 'r-', label='Validation Accuracy')
    axes[0, 0].set_title('Model Accuracy')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Accuracy')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Loss plot
    axes[0, 1].plot(epochs, history['loss'], 'b-', label='Training Loss')
    axes[0, 1].plot(epochs, history['val_loss'], 'r-', label='Validation Loss')
    axes[0, 1].set_title('Model Loss')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Accuracy comparison
    final_train_acc = history['accuracy'][-1]
    final_val_acc = history['val_accuracy'][-1]
    
    axes[1, 0].bar(['Training', 'Validation'], [final_train_acc, final_val_acc], 
                   color=['blue', 'red'], alpha=0.7)
    axes[1, 0].set_title('Final Accuracy Comparison')
    axes[1, 0].set_ylabel('Accuracy')
    axes[1, 0].set_ylim(0, 1)
    
    # Add accuracy values on bars
    axes[1, 0].text(0, final_train_acc + 0.01, f'{final_train_acc:.3f}', 
                    ha='center', va='bottom')
    axes[1, 0].text(1, final_val_acc + 0.01, f'{final_val_acc:.3f}', 
                    ha='center', va='bottom')
    
    # Loss comparison
    final_train_loss = history['loss'][-1]
    final_val_loss = history['val_loss'][-1]
    
    axes[1, 1].bar(['Training', 'Validation'], [final_train_loss, final_val_loss], 
                   color=['blue', 'red'], alpha=0.7)
    axes[1, 1].set_title('Final Loss Comparison')
    axes[1, 1].set_ylabel('Loss')
    
    # Add loss values on bars
    axes[1, 1].text(0, final_train_loss + 0.01, f'{final_train_loss:.3f}', 
                    ha='center', va='bottom')
    axes[1, 1].text(1, final_val_loss + 0.01, f'{final_val_loss:.3f}', 
                    ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('training_plots.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    logger.info("🧪 FlavorCraft Model Evaluation")
    logger.info("📍 Make sure you're running this from the 'cooking' root directory")
    
    # Check if we're in the right directory
    if not Path("data").exists() or not Path("models").exists():
        logger.error("❌ Please run this script from the 'cooking' root directory")
        logger.error("Expected structure:")
        logger.error("  cooking/")
        logger.error("  ├── data/data1/images/")
        logger.error("  ├── models/")
        logger.error("  └── evaluate_model.py")
        exit(1)
    
    success = evaluate_model_accuracy()
    if not success:
        exit(1)