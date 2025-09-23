#!/usr/bin/env python3
"""
FlavorCraft Development Startup Script
Enhanced for backend folder structure and dataset integration
"""

import subprocess
import os
import sys
import time
import threading
import signal
from pathlib import Path
import json

class FlavorCraftDev:
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.backend_dir = self.current_dir / "backend"  # Add backend directory
        self.processes = []
        self.backend_process = None
        self.frontend_process = None
        
    def check_system_requirements(self):
        """Check system requirements for FlavorCraft"""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print(f"❌ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        
        return True
    
    def check_project_structure(self):
        """Check project structure and locate backend files"""
        print("📁 Checking project structure...")
        
        # Check for backend folder structure
        if self.backend_dir.exists():
            print(f"✅ Backend folder found: {self.backend_dir}")
            
            # Check for app.py in backend folder
            if (self.backend_dir / "app.py").exists():
                print("✅ app.py found in backend folder")
                return True
            else:
                print("❌ app.py not found in backend folder")
                return False
        
        # Check for app.py in root
        elif (self.current_dir / "app.py").exists():
            print("✅ app.py found in root directory")
            self.backend_dir = self.current_dir  # Use root as backend
            return True
        
        else:
            print("❌ app.py not found in backend/ or root directory")
            print("📝 Expected structure:")
            print("   FlavorCraft/")
            print("   ├── backend/")
            print("   │   ├── app.py")
            print("   │   ├── image_model.py")
            print("   │   └── audio_model.py")
            print("   ├── src/ (React frontend)")
            print("   └── start-dev.py")
            return False
    
    def check_dataset(self):

        print("📊 Checking dataset availability...")
    
    # Updated dataset paths to match your structure
        dataset_paths = [
        # Your exact structure: cooking/data/archive (14)/images/
            self.current_dir / "data" / "archive (14)" / "images",
        
        # Alternative locations (fallbacks)
            self.current_dir / "data" / "archive" / "images",
            self.backend_dir / "data" / "archive (14)" / "images",
            self.backend_dir / "data" / "archive" / "images",
            self.current_dir / "backend" / "data" / "archive (14)" / "images",
            self.current_dir / "backend" / "data" / "archive" / "images"
        ]
    
        for dataset_path in dataset_paths:
            if dataset_path.exists():
                food_categories = [f.name for f in dataset_path.iterdir() if f.is_dir()]
                total_images = 0
            
                for category_dir in dataset_path.iterdir():
                    if category_dir.is_dir():
                        image_files = []
                    # Check for multiple image formats
                        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']:
                            image_files.extend(list(category_dir.glob(ext)))
                            image_files.extend(list(category_dir.glob(ext.upper())))
                        total_images += len(image_files)
            
                print(f"✅ Dataset found at: {dataset_path}")
                print(f"📊 {len(food_categories)} food categories, ~{total_images} images")
            
            # Show sample categories
                if food_categories:
                    sample_categories = food_categories[:5]
                    print(f"📋 Sample categories: {', '.join(sample_categories)}")
                    if len(food_categories) > 5:
                        print(f"    ... and {len(food_categories) - 5} more")
            
                return True
    
        print(f"⚠️  Dataset not found at any expected location")
        print("📝 Expected dataset location:")
        print("   cooking/data/archive (14)/images/")
        print("   └── pizza/")
        print("   └── burger/") 
        print("   └── pasta/")
        print("   └── ...")
        print("🔄 FlavorCraft will use fallback categories if dataset is missing")
        return False
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("🔍 Checking Python dependencies...")
        
        required_packages = {
            'flask': 'Flask web framework',
            'flask_cors': 'CORS support',
            'tensorflow': 'Deep learning framework',
            'PIL': 'Image processing',
            'numpy': 'Numerical computing',
            'google.generativeai': 'Gemini AI'
        }
        
        missing_packages = []
        
        for package, description in required_packages.items():
            try:
                __import__(package)
                print(f"  ✅ {package} - {description}")
            except ImportError:
                print(f"  ❌ {package} - {description}")
                missing_packages.append(package)
        
        # Check optional packages
        optional_packages = {
            'speech_recognition': 'Speech recognition',
            'pydub': 'Audio processing'
        }
        
        for package, description in optional_packages.items():
            try:
                __import__(package)
                print(f"  ✅ {package} - {description}")
            except ImportError:
                print(f"  ⚠️  {package} - {description} (optional)")
        
        if missing_packages:
            print(f"\n⚠️  Missing required packages: {', '.join(missing_packages)}")
            print("📦 Install with: pip install -r requirements.txt")
            return False
        
        print("✅ All required dependencies available")
        return True
    
    def check_npm(self):
        """Check Node.js and npm"""
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            npm_version = result.stdout.strip()
            
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            node_version = result.stdout.strip()
            
            print(f"✅ Node.js {node_version}, npm {npm_version}")
            return True
        except FileNotFoundError:
            print("❌ Node.js/npm not found")
            print("📦 Install Node.js from: https://nodejs.org/")
            return False
    
    def start_backend(self):
        """Start Flask backend with ML models"""
        print("🚀 Starting Flask backend with ML models...")
        
        # Check for app.py in backend directory
        backend_app_path = self.backend_dir / "app.py"
        
        if not backend_app_path.exists():
            print(f"❌ app.py not found at: {backend_app_path}")
            print("📝 Expected locations:")
            print(f"   • {self.backend_dir / 'app.py'}")
            print(f"   • {self.current_dir / 'app.py'}")
            return False
        
        print(f"✅ Found app.py at: {backend_app_path}")
        
        try:
            env = os.environ.copy()
            env.update({
                'FLASK_APP': 'app.py',
                'FLASK_ENV': 'development',
                'FLASK_DEBUG': '1',
                'PYTHONPATH': str(self.backend_dir)  # Set Python path to backend directory
            })
            
            # Start backend from the backend directory
            self.backend_process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=self.backend_dir,  # Run from backend directory
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            print(f"✅ Backend started (PID: {self.backend_process.pid})")
            print(f"📁 Working directory: {self.backend_dir}")
            print("📡 Backend URL: http://localhost:5007")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start React frontend"""
        print("🎨 Starting React frontend...")
        
        # Look for package.json in multiple locations
        frontend_paths = [
            self.current_dir,  # Root directory
            self.current_dir / "frontend",  # Frontend folder
            self.current_dir / "src"  # Src folder
        ]
        
        package_json_path = None
        frontend_dir = None
        
        for path in frontend_paths:
            if (path / "package.json").exists():
                package_json_path = path / "package.json"
                frontend_dir = path
                break
        
        if not package_json_path:
            print("❌ package.json not found")
            print("📝 Looked in:")
            for path in frontend_paths:
                print(f"   • {path / 'package.json'}")
            return False
        
        print(f"✅ Found package.json at: {package_json_path}")
        
        # Install npm dependencies if needed
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing npm dependencies...")
            try:
                subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
                print("✅ npm dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ npm install failed: {e}")
                return False
        
        try:
            env = os.environ.copy()
            env.update({
                'BROWSER': 'none',
                'REACT_APP_BACKEND_URL': 'http://localhost:5007'
            })
            
            self.frontend_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=frontend_dir,  # Run from frontend directory
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            print(f"✅ Frontend started (PID: {self.frontend_process.pid})")
            print(f"📁 Working directory: {frontend_dir}")
            print("🌐 Frontend URL: http://localhost:3000")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor backend and frontend processes"""
        def monitor_backend():
            startup_messages_shown = False
            
            for line in iter(self.backend_process.stdout.readline, ''):
                if line.strip():
                    print(f"🔧 Backend: {line.strip()}")
                    
                    # Check for key startup messages
                    if not startup_messages_shown:
                        if "Image model" in line or "image model" in line:
                            print("📸 Image classification model ready")
                        elif "Audio model" in line or "audio model" in line:
                            print("🎙️  Speech recognition model ready") 
                        elif "Gemini model" in line or "gemini model" in line:
                            print("🤖 Gemini AI model ready")
                        elif "STARTING FLAVORCRAFT" in line or "Starting FlavorCraft" in line:
                            print("✅ FlavorCraft backend fully initialized!")
                            startup_messages_shown = True
        
        def monitor_frontend():
            startup_complete = False
            
            for line in iter(self.frontend_process.stdout.readline, ''):
                if line.strip():
                    print(f"🎨 Frontend: {line.strip()}")
                    
                    if not startup_complete and ("compiled successfully" in line.lower() or "webpack compiled" in line.lower()):
                        print("✅ Frontend compilation complete!")
                        startup_complete = True
        
        # Start monitoring threads
        if self.backend_process:
            backend_thread = threading.Thread(target=monitor_backend, daemon=True)
            backend_thread.start()
        
        if self.frontend_process:
            frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
            frontend_thread.start()
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Shutting down FlavorCraft...")
        
        if self.backend_process:
            print("🔧 Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
                print("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing backend...")
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🎨 Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
                print("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing frontend...")
                self.frontend_process.kill()
    
    def run(self):
        """Main run function"""
        print("🍕" * 25)
        print("🚀 FLAVORCRAFT DEVELOPMENT SERVER")
        print("🍕" * 25)
        print("🤖 Multi-modal Recipe Generation Platform")
        print("📊 Custom Dataset + Speech + Vision + AI")
        print("🍕" * 25)
        
        # Pre-flight checks
        if not self.check_system_requirements():
            sys.exit(1)
        
        if not self.check_project_structure():
            sys.exit(1)
        
        if not self.check_dependencies():
            sys.exit(1)
        
        if not self.check_npm():
            sys.exit(1)
        
        # Check dataset (non-blocking)
        self.check_dataset()
        
        # Start services
        print("\n🚀 Starting FlavorCraft services...")
        
        if not self.start_backend():
            sys.exit(1)
        
        # Wait for backend to initialize
        time.sleep(5)
        
        if not self.start_frontend():
            print("⚠️  Frontend failed to start, running backend only")
        
        # Monitor processes
        self.monitor_processes()
        
        # Show status
        time.sleep(3)
        print("\n" + "="*60)
        print("🎉 FLAVORCRAFT IS RUNNING!")
        print("="*60)
        print("🔧 Backend API: http://localhost:5007")
        print("🎨 Frontend UI: http://localhost:3000")
        print("")
        print("🎯 Features Available:")
        print("   📸 Image Food Classification")
        print("   🎙️  Speech-to-Text Processing")  
        print("   📝 Text Ingredient Analysis")
        print("   🤖 AI Recipe Generation")
        print("")
        print("📁 Project Structure:")
        print(f"   🔧 Backend: {self.backend_dir}")
        print(f"   🎨 Frontend: {self.current_dir}")
        print(f"   📊 Dataset: Looking for data/archive/images/")
        print("")
        print("💡 Usage:")
        print("   1. Enter available ingredients")
        print("   2. Upload a food image")
        print("   3. Record cooking preferences")
        print("   4. Get AI-generated recipe!")
        print("="*60)
        print("💡 Press Ctrl+C to stop all services")
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running
        try:
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died unexpectedly")
                    break
                    
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died unexpectedly")
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    dev_server = FlavorCraftDev()
    dev_server.run()
