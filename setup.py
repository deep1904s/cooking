#!/usr/bin/env python3
"""
Setup script for FlavorCraft - Multimodal Recipe Generator
Run this script to set up the environment and download required models
"""

import os
import sys
import subprocess
import logging
import nltk
import tensorflow as tf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def install_system_dependencies():
    """Install system dependencies"""
    logger.info("Installing system dependencies...")
    
    try:
        # For Ubuntu/Debian systems
        if os.path.exists('/etc/debian_version'):
            subprocess.run([
                'sudo', 'apt-get', 'update'
            ], check=True)
            subprocess.run([
                'sudo', 'apt-get', 'install', '-y',
                'portaudio19-dev',  # For pyaudio
                'ffmpeg',           # For audio processing
                'python3-dev',      # For building Python extensions
                'build-essential'   # For compiling dependencies
            ], check=True)
            logger.info("✓ System dependencies installed")
        
        # For macOS
        elif sys.platform == 'darwin':
            # Check if brew is installed
            try:
                subprocess.run(['brew', '--version'], check=True, capture_output=True)
                subprocess.run(['brew', 'install', 'portaudio', 'ffmpeg'], check=True)
                logger.info("✓ System dependencies installed via Homebrew")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("Homebrew not found. Please install manually:")
                logger.warning("  brew install portaudio ffmpeg")
        
        # For Windows
        elif sys.platform == 'win32':
            logger.info("Windows detected. Please ensure you have:")
            logger.info("1. Visual Studio Build Tools installed")
            logger.info("2. FFmpeg installed and in PATH")
            logger.info("3. PortAudio installed")
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to install some system dependencies: {e}")
        logger.warning("You may need to install them manually")

def install_python_dependencies():
    """Install Python dependencies"""
    logger.info("Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True)
        
        # Install requirements
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        
        logger.info("✓ Python dependencies installed")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Python dependencies: {e}")
        return False
    
    return True

def download_nltk_data():
    """Download required NLTK data"""
    logger.info("Downloading NLTK data...")
    
    try:
        # Download required NLTK datasets
        nltk_downloads = [
            'punkt',
            'stopwords',
            'averaged_perceptron_tagger',
            'wordnet',
            'omw-1.4'
        ]
        
        for dataset in nltk_downloads:
            try:
                nltk.download(dataset, quiet=True)
                logger.info(f"✓ Downloaded NLTK {dataset}")
            except Exception as e:
                logger.warning(f"Failed to download NLTK {dataset}: {e}")
        
        logger.info("✓ NLTK data downloads completed")
        
    except Exception as e:
        logger.error(f"Error downloading NLTK data: {e}")

def verify_tensorflow_installation():
    """Verify TensorFlow installation and GPU support"""
    logger.info("Verifying TensorFlow installation...")
    
    try:
        # Check TensorFlow version
        logger.info(f"TensorFlow version: {tf.__version__}")
        
        # Check for GPU support
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            logger.info(f"✓ Found {len(gpus)} GPU(s)")
            for gpu in gpus:
                logger.info(f"  - {gpu}")
        else:
            logger.info("No GPU found, will use CPU")
        
        # Test basic TensorFlow operations
        tf.constant([1, 2, 3])
        logger.info("✓ TensorFlow is working correctly")
        
    except Exception as e:
        logger.error(f"TensorFlow verification failed: {e}")

def create_directories():
    """Create necessary directories"""
    logger.info("Creating directories...")
    
    directories = [
        'models',
        'uploads',
        'temp',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

def create_env_file():
    """Create .env file with default configuration"""
    logger.info("Creating .env file...")
    
    env_content = """# FlavorCraft Configuration

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True
PORT=5000

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
UPLOAD_FOLDER=temp

# Model Configuration
USE_GPU=True
MODEL_CACHE_DIR=models

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/flavorcraft.log

# API Configuration
API_TIMEOUT=300  # 5 minutes
MAX_WORKERS=4
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("✓ Created .env file")
    else:
        logger.info("✓ .env file already exists")

def run_tests():
    """Run basic tests to verify setup"""
    logger.info("Running basic tests...")
    
    try:
        # Test imports
        from audio_model import AudioModel
        from image_model import ImageModel
        from text_model import TextModel
        
        # Test model initialization
        logger.info("Testing model initialization...")
        
        try:
            audio_model = AudioModel()
            logger.info("✓ Audio model initialized")
        except Exception as e:
            logger.warning(f"Audio model initialization failed: {e}")
        
        try:
            image_model = ImageModel()
            logger.info("✓ Image model initialized")
        except Exception as e:
            logger.warning(f"Image model initialization failed: {e}")
        
        try:
            text_model = TextModel()
            logger.info("✓ Text model initialized")
        except Exception as e:
            logger.warning(f"Text model initialization failed: {e}")
        
        logger.info("✓ Basic tests completed")
        
    except ImportError as e:
        logger.error(f"Import error during testing: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    logger.info("=== FlavorCraft Setup ===")
    logger.info("Setting up FlavorCraft Multimodal Recipe Generator...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    logger.info(f"Python version: {sys.version}")
    
    # Setup steps
    steps = [
        ("Installing system dependencies", install_system_dependencies),
        ("Installing Python dependencies", install_python_dependencies),
        ("Downloading NLTK data", download_nltk_data),
        ("Verifying TensorFlow", verify_tensorflow_installation),
        ("Creating directories", create_directories),
        ("Creating configuration file", create_env_file),
        ("Running tests", run_tests)
    ]
    
    for step_name, step_func in steps:
        logger.info(f"\n--- {step_name} ---")
        try:
            result = step_func()
            if result is False:
                logger.error(f"Setup failed at: {step_name}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error in {step_name}: {e}")
            sys.exit(1)
    
    logger.info("\n=== Setup Complete ===")
    logger.info("FlavorCraft setup completed successfully!")
    logger.info("\nTo start the server, run:")
    logger.info("  python app.py")
    logger.info("\nTo start the React frontend, run:")
    logger.info("  npm start")

if __name__ == '__main__':
    main()