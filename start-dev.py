#!/usr/bin/env python3
"""
FlavorCraft Development Startup Script
Runs both backend and frontend with a single command
"""

import subprocess
import os
import sys
import time
import threading
from pathlib import Path
import json

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    # Check Python dependencies
    try:
        import flask
        import flask_cors
        print("Flask dependencies found")
    except ImportError:
        print("Missing Flask dependencies. Run: pip install flask flask-cors")
        return False
    
    # Check if npm is available
    try:
        subprocess.run(['npm', '--version'], capture_output=True, check=True)
        print("npm found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("npm not found. Please install Node.js and npm")
        return False
    
    return True

def setup_frontend():
    """Set up frontend files if needed"""
    print("Setting up frontend...")
    
    current_dir = Path(__file__).parent
    
    # Create directories
    (current_dir / "src").mkdir(exist_ok=True)
    (current_dir / "public").mkdir(exist_ok=True)
    
    # Check if package.json exists
    package_json_path = current_dir / "package.json"
    
    if not package_json_path.exists():
        print("Creating package.json...")
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
            "proxy": "http://localhost:5007"
        }
        
        with open(package_json_path, 'w') as f:
            json.dump(package_json, f, indent=2)
        print("Created package.json")
    
    # Create public/index.html
    public_index = current_dir / "public" / "index.html"
    if not public_index.exists():
        print("Creating index.html...")
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
        print("Created public/index.html")
    
    # Create src/index.js if it doesn't exist
    src_index = current_dir / "src" / "index.js"
    if not src_index.exists() and not (current_dir / "App.js").exists():
        print("Creating src/index.js...")
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
        with open(src_index, 'w') as f:
            f.write(js_content)
        print("Created src/index.js")
    
    # Create src/index.css
    src_css = current_dir / "src" / "index.css"
    if not src_css.exists() and not (current_dir / "index.css").exists():
        print("Creating src/index.css...")
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
        with open(src_css, 'w') as f:
            f.write(css_content)
        print("Created src/index.css")
    
    # Check for App.js in root or src
    app_js_root = current_dir / "App.js"
    app_js_src = current_dir / "src" / "App.js"
    
    if app_js_root.exists() and not app_js_src.exists():
        print("Moving App.js to src/ directory...")
        app_js_root.rename(app_js_src)
    
    # Check for other files that might need to be moved to src/
    files_to_move = ["App.css", "index.css"]
    for file_name in files_to_move:
        root_file = current_dir / file_name
        src_file = current_dir / "src" / file_name
        if root_file.exists() and not src_file.exists():
            print(f"Moving {file_name} to src/ directory...")
            root_file.rename(src_file)
    
    print("Frontend setup complete")

def run_backend():
    """Run the Flask backend server"""
    print("Starting Flask backend on http://localhost:5007")
    
    current_dir = Path(__file__).parent
    
    # Look for app.py in current directory
    app_py_path = current_dir / "app.py"
    if not app_py_path.exists():
        print("app.py not found in current directory!")
        return
    
    # Start Flask app
    env = os.environ.copy()
    env['FLASK_APP'] = 'app.py'
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    env['PORT'] = '5007'
    env['PYTHONPATH'] = str(current_dir)
    
    try:
        subprocess.run([
            sys.executable, str(app_py_path)
        ], env=env, cwd=current_dir)
    except KeyboardInterrupt:
        print("\nBackend stopped")

def run_frontend():
    """Run the React frontend server"""
    print("Starting React frontend on http://localhost:3000")
    
    current_dir = Path(__file__).parent
    
    try:
        # Change to current directory
        os.chdir(current_dir)
        
        # Install dependencies if node_modules doesn't exist
        if not os.path.exists('node_modules'):
            print("Installing npm dependencies...")
            subprocess.run(['npm', 'install'], check=True)
        
        # Start React development server
        subprocess.run(['npm', 'start'])
    except subprocess.CalledProcessError as e:
        print(f"Error starting React app: {e}")
        print("Make sure Node.js and npm are installed.")
    except KeyboardInterrupt:
        print("\nFrontend stopped")

def install_frontend_deps():
    """Install frontend dependencies"""
    print("Installing frontend dependencies...")
    
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    try:
        if os.path.exists('package.json') and not os.path.exists('node_modules'):
            subprocess.run(['npm', 'install'], check=True)
            print("Frontend dependencies installed")
        else:
            print("Dependencies already installed or package.json missing")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install frontend dependencies: {e}")

def main():
    """Main function to start both servers"""
    print("Starting FlavorCraft Development Environment")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        return
    
    # Setup frontend
    setup_frontend()
    
    # Install frontend dependencies
    install_frontend_deps()
    
    print("\nStarting services...")
    print("Backend: http://localhost:5007")
    print("Frontend: http://localhost:3000")
    print("\nPress Ctrl+C to stop both services\n")
    
    # Start both servers in separate threads
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    
    try:
        # Start backend first
        backend_thread.start()
        print("Waiting for backend to start...")
        time.sleep(3)
        
        # Start frontend
        frontend_thread.start()
        print("Waiting for frontend to start...")
        time.sleep(2)
        
        print("\n" + "=" * 50)
        print("FlavorCraft is running!")
        print("Frontend: http://localhost:3000")
        print("Backend:  http://localhost:5007")
        print("=" * 50)
        print("Press Ctrl+C to stop both servers")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down FlavorCraft...")
        print("Goodbye!")

if __name__ == '__main__':
    main()