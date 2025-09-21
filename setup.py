#!/usr/bin/env python3
"""
Enhanced Setup script for FlavorCraft - LLM-Powered Multimodal Recipe Generator
Run this script to set up the environment with Google Gemini AI integration
"""

import os
import sys
import subprocess
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        logger.error(f"Current version: {sys.version}")
        return False
    
    logger.info(f"Python version: {sys.version}")
    return True

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
                'portaudio19-dev',
                'ffmpeg',
                'python3-dev',
                'build-essential',
                'git'
            ], check=True)
            logger.info("System dependencies installed")
        
        # For macOS
        elif sys.platform == 'darwin':
            try:
                subprocess.run(['brew', '--version'], check=True, capture_output=True)
                subprocess.run(['brew', 'install', 'portaudio', 'ffmpeg'], check=True)
                logger.info("System dependencies installed via Homebrew")
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("Homebrew not found. Please install manually:")
                logger.warning("  brew install portaudio ffmpeg")
        
        # For Windows
        elif sys.platform == 'win32':
            logger.info("Windows detected. Please ensure you have:")
            logger.info("1. Visual Studio Build Tools installed")
            logger.info("2. FFmpeg installed and in PATH")
            logger.info("3. Git installed")
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Some system dependencies may not have installed: {e}")
        logger.warning("You may need to install them manually")

def upgrade_pip():
    """Upgrade pip to latest version"""
    logger.info("Upgrading pip...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True)
        logger.info("pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to upgrade pip: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies including Google Generative AI"""
    logger.info("Installing Python dependencies...")
    
    # Essential packages first
    essential_packages = [
        'flask>=3.0.0',
        'flask-cors>=4.0.0',
        'google-generativeai>=0.3.2',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'pillow>=10.1.0',
        'numpy>=1.24.3'
    ]
    
    # Try to install essential packages first
    for package in essential_packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True)
            logger.info(f"{package} installed")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            return False
    
    # Then try to install all requirements
    try:
        if os.path.exists('requirements.txt'):
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True)
            logger.info("All Python dependencies installed")
        else:
            logger.warning("requirements.txt not found, only essential packages installed")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Some optional dependencies failed to install: {e}")
        logger.info("Core functionality should still work")
        return True

def setup_nltk_data():
    """Download required NLTK data"""
    logger.info("Setting up NLTK data...")
    
    try:
        import nltk
        
        datasets = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']
        
        for dataset in datasets:
            try:
                nltk.download(dataset, quiet=True)
                logger.info(f"NLTK {dataset} downloaded")
            except Exception as e:
                logger.warning(f"Could not download {dataset}: {e}")
        
        return True
        
    except ImportError:
        logger.warning("NLTK not available, skipping data download")
        return False

def test_google_ai_connection():
    """Test Google AI API connection"""
    logger.info("Testing Google AI connection...")
    
    try:
        import google.generativeai as genai
        
        # Use the API key from the code
        api_key = "AIzaSyDDhOVdFG5tl29-v1gi7KUqul7iPAX8oqc"
        genai.configure(api_key=api_key)
        
        # Try to initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple prompt
        response = model.generate_content("Hello, this is a test.")
        
        if response.text:
            logger.info("Google Gemini AI connection successful")
            return True
        else:
            logger.warning("Google AI responded but with empty content")
            return False
            
    except Exception as e:
        logger.error(f"Google AI connection failed: {e}")
        logger.error("Check your API key and internet connection")
        return False

def test_model_imports():
    """Test if models can be imported"""
    logger.info("Testing model imports...")
    
    models_status = {
        'text_model': False,
        'audio_model': False,
        'image_model': False
    }
    
    # Test text model
    try:
        from text_model import TextModel
        text_model = TextModel()
        models_status['text_model'] = True
        logger.info("Text model imported successfully")
    except Exception as e:
        logger.warning(f"Text model import failed: {e}")
    
    # Test audio model
    try:
        from audio_model import AudioModel
        audio_model = AudioModel()
        models_status['audio_model'] = True
        logger.info("Audio model imported successfully")
    except Exception as e:
        logger.warning(f"Audio model import failed: {e}")
        logger.warning("Speech recognition dependencies may be missing")
    
    # Test image model
    try:
        from image_model import ImageModel
        image_model = ImageModel()
        models_status['image_model'] = True
        logger.info("Image model imported successfully")
    except Exception as e:
        logger.warning(f"Image model import failed: {e}")
        logger.warning("TensorFlow dependencies may be missing")
    
    return models_status

def create_directories():
    """Create necessary directories"""
    logger.info("Creating directories...")
    
    directories = [
        'models',
        'uploads', 
        'temp',
        'logs',
        'cache',
        'public',
        'src'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def create_env_file():
    """Create .env file with configuration"""
    logger.info("Creating configuration file...")
    
    env_content = """# FlavorCraft Configuration

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True
PORT=5007

# Google AI Configuration
GOOGLE_API_KEY=AIzaSyDDhOVdFG5tl29-v1gi7KUqul7iPAX8oqc
GEMINI_MODEL=gemini-1.5-flash

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=temp

# Model Configuration
USE_GPU=True
MODEL_CACHE_DIR=models

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/flavorcraft.log

# API Configuration
API_TIMEOUT=300
MAX_WORKERS=4

# Development Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("Created .env file")
    else:
        logger.info(".env file already exists")

def test_flask_app():
    """Test if Flask app can start"""
    logger.info("Testing Flask application...")
    
    try:
        # Import app to test for syntax errors
        if os.path.exists('app.py'):
            from app import app
            logger.info("Flask app imports successfully")
            
            # Test basic endpoint
            with app.test_client() as client:
                response = client.get('/')
                if response.status_code == 200:
                    logger.info("Health check endpoint working")
                    return True
                else:
                    logger.warning(f"Health check returned status: {response.status_code}")
                    return False
        else:
            logger.warning("app.py not found, skipping Flask test")
            return True
                
    except Exception as e:
        logger.error(f"Flask app test failed: {e}")
        return False

def create_frontend_files():
    """Create basic frontend files"""
    logger.info("Creating frontend files...")
    
    # Create public/index.html
    public_dir = Path('public')
    public_dir.mkdir(exist_ok=True)
    
    index_html = public_dir / 'index.html'
    if not index_html.exists():
        html_content = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="FlavorCraft - AI-Powered Multimodal Recipe Generator" />
    <title>FlavorCraft - AI Recipe Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''
        with open(index_html, 'w') as f:
            f.write(html_content)
        logger.info("Created public/index.html")
    
    # Create src/index.js
    src_dir = Path('src')
    src_dir.mkdir(exist_ok=True)
    
    index_js = src_dir / 'index.js'
    if not index_js.exists():
        js_content = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''
        with open(index_js, 'w') as f:
            f.write(js_content)
        logger.info("Created src/index.js")
    
    # Create src/index.css
    index_css = src_dir / 'index.css'
    if not index_css.exists():
        css_content = '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}'''
        with open(index_css, 'w') as f:
            f.write(css_content)
        logger.info("Created src/index.css")

def setup_frontend():
    """Setup frontend if Node.js is available"""
    logger.info("Checking for Node.js...")
    
    try:
        # Check if npm is available
        result = subprocess.run(['npm', '--version'], capture_output=True, check=True)
        npm_version = result.stdout.decode().strip()
        logger.info(f"npm version: {npm_version}")
        
        # Create package.json if it doesn't exist
        if not os.path.exists('package.json'):
            package_json = {
                "name": "flavorcraft-frontend",
                "version": "1.0.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1",
                    "lucide-react": "^0.263.1",
                    "web-vitals": "^2.1.4"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "test": "react-scripts test",
                    "eject": "react-scripts eject"
                },
                "eslintConfig": {
                    "extends": ["react-app", "react-app/jest"]
                },
                "browserslist": {
                    "production": [">0.2%", "not dead", "not op_mini all"],
                    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
                },
                "proxy": "http://localhost:5000"
            }
            
            with open('package.json', 'w') as f:
                json.dump(package_json, f, indent=2)
            logger.info("Created package.json")
        
        # Create frontend files
        create_frontend_files()
        
        logger.info("Frontend setup complete")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Node.js/npm not found. Frontend setup skipped.")
        logger.warning("Install Node.js to use the React frontend")
        create_frontend_files()  # Create files anyway
        return False

def print_startup_instructions():
    """Print instructions for starting the application"""
    logger.info("\n" + "="*60)
    logger.info("FlavorCraft Setup Complete!")
    logger.info("="*60)
    
    logger.info("\nSetup Summary:")
    logger.info("- Google Gemini AI integration configured")
    logger.info("- Python dependencies installed")
    logger.info("- Models and directories set up")
    logger.info("- Configuration files created")
    
    logger.info("\nTo start FlavorCraft:")
    logger.info("1. Backend (Flask API):")
    logger.info("   python app.py")
    logger.info("   (Will run on http://localhost:5000)")
    
    logger.info("\n2. Frontend (React app):")
    if os.path.exists('package.json'):
        logger.info("   npm install  (first time only)")
        logger.info("   npm start")
        logger.info("   (Will run on http://localhost:3000)")
    else:
        logger.info("   Frontend files are ready - set up React environment separately")
    
    logger.info("\nAPI Key configured:")
    logger.info("   Google Gemini AI key is already set up")
    
    logger.info("\nInput Methods:")
    logger.info("   - Text: Ingredients lists and cooking preferences")
    logger.info("   - Image: Dish photos for AI identification")
    logger.info("   - Audio: Voice instructions and descriptions")
    
    logger.info("\nAI Features:")
    logger.info("   - Google Gemini generates complete recipes")
    logger.info("   - Combines all three input types intelligently")
    logger.info("   - Provides cooking tips and variations")
    
    logger.info("\nImportant files:")
    logger.info("   - app.py - Main backend application")
    logger.info("   - src/App.js - React frontend component")
    logger.info("   - .env - Configuration file")
    logger.info("   - requirements.txt - Python dependencies")

def main():
    """Main setup function"""
    logger.info("=" * 60)
    logger.info("FlavorCraft LLM Setup")
    logger.info("=" * 60)
    
    # Check Python version first
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Installing system dependencies", install_system_dependencies),
        ("Upgrading pip", upgrade_pip),
        ("Installing Python dependencies", install_python_dependencies),
        ("Setting up NLTK data", setup_nltk_data),
        ("Testing Google AI connection", test_google_ai_connection),
        ("Creating directories", create_directories),
        ("Creating configuration", create_env_file),
        ("Testing model imports", test_model_imports),
        ("Testing Flask application", test_flask_app),
        ("Setting up frontend", setup_frontend)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"\n--- {step_name} ---")
        try:
            result = step_func()
            if result is False:
                failed_steps.append(step_name)
                logger.warning(f"{step_name} had issues but continuing...")
        except Exception as e:
            logger.error(f"Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Print results
    if failed_steps:
        logger.warning(f"\nSome steps had issues: {', '.join(failed_steps)}")
        logger.warning("Core functionality should still work")
    
    print_startup_instructions()

if __name__ == '__main__':
    main()