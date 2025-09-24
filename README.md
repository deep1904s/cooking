# FlavorCraft 🍳✨
*Smart Recipe Curation Platform - AI-Powered Multimodal Recipe Generator*

## Project Overview

FlavorCraft is an innovative culinary platform that leverages Google Gemini AI to transform your available ingredients, food images, and voice preferences into personalized, detailed recipes. By combining multiple input modalities (text, image, and audio), FlavorCraft creates a truly intelligent cooking assistant that understands not just what you have, but how you want to cook.

## 🎯 Core Concept

### The Problem
- Traditional recipe apps require you to search for specific dishes
- Ingredient-based searches often yield generic results
- No consideration for cooking skill level, dietary preferences, or available equipment
- Limited personalization and contextual understanding

### The FlavorCraft Solution
FlavorCraft flips the script by being **ingredient-centric** and **preference-aware**:

1. **Tell us what you have** - List your available ingredients
2. **Show us your inspiration** - Upload photos of dishes you'd like to recreate
3. **Express your preferences** - Use voice commands to specify dietary needs, cooking style, or skill level
4. **Receive intelligent curation** - Get personalized recipes that match your exact situation

## 🏗️ Technical Architecture

### Backend (Flask API)
- **Framework**: Flask with CORS support
- **AI Integration**: Google Gemini 1.5 Flash model
- **Port**: 5007
- **Key Features**:
  - Multimodal input processing
  - Real-time recipe generation
  - Intelligent ingredient analysis
  - Voice command interpretation
  - Image recognition for food identification

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Styling**: Tailwind CSS for responsive design
- **Icons**: Lucide React for beautiful UI elements
- **Port**: 3000 (proxies to backend on 5007)
- **Features**:
  - Interactive ingredient input
  - Drag-and-drop image uploads
  - Voice recording interface
  - Real-time recipe display
  - Enhanced user experience with animations

### AI Models Integration
- **Primary**: Google Gemini 1.5 Flash for recipe generation
- **Text Processing**: NLTK for ingredient parsing and analysis
- **Image Analysis**: Computer vision for food identification
- **Audio Processing**: Speech-to-text for voice commands

## 🌟 Key Features

### Multimodal Input System
1. **Text Input**: 
   - Ingredient lists with quantities
   - Dietary restrictions and preferences
   - Cooking skill level specification

2. **Image Input**:
   - Food photos for dish identification
   - Ingredient recognition from pantry photos
   - Plating style preferences

3. **Voice Input**:
   - Natural language cooking preferences
   - Dietary restrictions via speech
   - Cooking method preferences

### Intelligent Recipe Generation
- **Context-Aware**: Considers available ingredients, equipment, and skill level
- **Personalized**: Adapts to dietary preferences and restrictions
- **Comprehensive**: Includes ingredients, instructions, timing, and tips
- **Scalable**: Adjusts serving sizes and ingredient quantities

### Enhanced User Experience
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Processing**: Immediate feedback and recipe generation
- **Interactive Interface**: Drag-and-drop, voice controls, and smooth animations
- **Smart Caching**: Efficient API usage and faster response times

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js & npm
- System dependencies (portaudio, ffmpeg)

### Quick Start
1. **Initial Setup** (run once):
   ```bash
   python setup.py
   ```

2. **Development Enhancement**:
   ```bash
   python start-dev.py
   ```

3. **Start Backend**:
   ```bash
   python app.py
   ```

4. **Start Frontend**:
   ```bash
   npm install  # first time only
   npm start
   ```

5. **Access Application**:
   - Frontend: http://localhost:3000
   - API: http://localhost:5007



## 🔧 Configuration

### Environment Variables
The setup script automatically creates a `.env` file with:
- Google Gemini API configuration
- Flask server settings
- File upload limits
- Model caching options
- Development vs production flags

### API Key Management
- Google Gemini AI key is pre-configured for immediate use
- All API calls are handled securely through environment variables
- Rate limiting and error handling built-in

## 🎨 User Interface Theory

### Design Philosophy
- **Ingredient-First**: The interface prioritizes ingredient input as the starting point
- **Multimodal Harmony**: Seamlessly integrates text, image, and voice inputs
- **Progressive Disclosure**: Advanced options are available but don't clutter the main flow
- **Responsive Feedback**: Real-time updates and visual feedback for all actions

### User Journey
1. **Landing**: Clean, inviting interface with clear call-to-action
2. **Input Collection**: Multiple ways to provide information (text, image, voice)
3. **Processing**: Visual feedback during AI analysis
4. **Results**: Beautiful recipe display with actionable information
5. **Iteration**: Easy modification and re-generation capabilities

## 🧠 AI Integration Theory

### Prompt Engineering
FlavorCraft uses sophisticated prompt engineering to:
- Combine multiple input types into coherent recipe requests
- Maintain context across different input modalities
- Generate comprehensive recipes with proper formatting
- Include cooking tips and variations

### Multimodal Fusion
- **Text Analysis**: Extracts ingredients, quantities, and preferences
- **Image Recognition**: Identifies foods, cooking styles, and presentations
- **Voice Processing**: Converts speech to structured recipe parameters
- **Context Integration**: Combines all inputs for holistic recipe generation

## 🎯 Use Cases

### Home Cooking
- "I have chicken, rice, and vegetables - what can I make?"
- Upload a photo of a dish you want to recreate
- Voice command: "Make it spicy and vegetarian-friendly"

### Meal Planning
- Weekly ingredient lists converted to daily meal suggestions
- Dietary restriction management across multiple recipes
- Batch cooking optimization

### Culinary Learning
- Skill-appropriate recipe suggestions
- Cooking technique explanations
- Progressive complexity as skills improve

### Special Diets
- Automatic adaptation for keto, vegan, gluten-free, etc.
- Allergen awareness and substitution suggestions
- Nutritional information integration

## 🔮 Future Enhancements

### Planned Features
- **Community Recipes**: User-generated content with AI curation
- **Shopping Integration**: Automatic grocery list generation
- **Nutrition Analysis**: Detailed nutritional breakdowns
- **Meal Planning**: Weekly/monthly meal planning assistance
- **Social Sharing**: Recipe sharing and collaboration features

### Technical Improvements
- **Advanced AI Models**: Integration of specialized food AI models
- **Real-time Collaboration**: Multiple users planning meals together
- **IoT Integration**: Smart kitchen appliance connectivity
- **Mobile App**: Native iOS/Android applications

## 📊 Performance & Scalability

### Current Capabilities
- Handles multiple concurrent users
- Efficient API usage with caching
- Responsive performance on modern devices
- Scalable architecture for growth

### Optimization Features
- **Smart Caching**: Reduces API calls for similar requests
- **Async Processing**: Non-blocking operations for better UX
- **Error Recovery**: Graceful handling of API limitations
- **Resource Management**: Efficient file handling and cleanup

## 🤝 Contributing

FlavorCraft is designed with extensibility in mind. Key areas for contribution:
- **AI Model Integration**: Adding new AI capabilities
- **Input Modalities**: Supporting new types of user input
- **Recipe Sources**: Integrating with recipe databases
- **UI/UX Improvements**: Enhancing the user experience
- **Performance Optimization**: Making the system faster and more efficient

## 📝 License & Usage

This project demonstrates advanced AI integration patterns and multimodal user interface design. It serves as both a functional cooking assistant and a reference implementation for modern AI application development.

---

*FlavorCraft - Where Ingredients Meet Intelligence* 🍳✨