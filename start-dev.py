#!/usr/bin/env python3
"""
FlavorCraft Development Startup Script
Runs both backend and frontend with a single command
"""

import subprocess
import os
import sys
import time
import signal
import threading
from pathlib import Path
import json

def setup_frontend():
    """Set up frontend if needed"""
    print("🔧 Setting up frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Create directories if they don't exist
    (frontend_dir / "src").mkdir(exist_ok=True)
    (frontend_dir / "public").mkdir(exist_ok=True)
    
    # Check if package.json exists and has correct structure
    package_json_path = frontend_dir / "package.json"
    
    if not package_json_path.exists():
        print("📦 Creating package.json...")
        package_json = {
            "name": "flavorcraft-frontend",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.16.4",
                "@testing-library/react": "^13.3.0",
                "@testing-library/user-event": "^13.5.0",
                "lucide-react": "^0.263.1",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
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
        
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
    
    # Create public/index.html if it doesn't exist
    public_index = frontend_dir / "public" / "index.html"
    if not public_index.exists():
        print("🌐 Creating index.html...")
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
        with open(public_index, 'w') as f:
            f.write(html_content)
    
    print("✅ Frontend setup complete")

def run_backend():
    """Run the Flask backend server"""
    print("🚀 Starting Flask backend on http://localhost:5000")
    backend_dir = Path(__file__).parent / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start Flask app
    env = os.environ.copy()
    env['FLASK_APP'] = 'app.py'
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    env['PYTHONPATH'] = str(backend_dir)
    
    try:
        subprocess.run([
            sys.executable, 'app.py'
        ], env=env)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")

def run_frontend():
    """Run the React frontend server"""
    print("🎨 Starting React frontend on http://localhost:3000")
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    try:
        # Install dependencies if node_modules doesn't exist
        if not os.path.exists('node_modules'):
            print("📦 Installing npm dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Start React development server
        subprocess.run(['npm', 'start'])
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting React app: {e}")
        print("Make sure Node.js and npm are installed.")
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python dependencies
    try:
        import flask
        import flask_cors
        print("✅ Flask dependencies found")
    except ImportError:
        print("❌ Missing Flask dependencies. Run: pip install flask flask-cors")
        return False
    
    # Check if npm is available
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        print("✅ npm found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm not found. Please install Node.js and npm")
        return False
    
    return True

def main():
    """Main function to start both servers"""
    print("🍳 Starting FlavorCraft Development Environment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        return
    
    # Setup frontend
    setup_frontend()
    
    # Start both servers in separate threads
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    try:
        # Start backend first
        backend_thread.start()
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Start frontend
        frontend_thread.start()
        print("⏳ Waiting for frontend to start...")
        time.sleep(2)
        
        print("\n" + "=" * 50)
        print("🎉 FlavorCraft is running!")
        print("🔗 Frontend: http://localhost:3000")
        print("🔗 Backend:  http://localhost:5000")
        print("=" * 50)
        print("Press Ctrl+C to stop both servers")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down FlavorCraft...")
        print("👋 Goodbye!")

if __name__ == '__main__':
    main()