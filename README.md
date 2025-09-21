# FlavorCraft - LLM-Powered Multimodal Recipe Generator

FlavorCraft is an AI-powered application that generates personalized recipes using three types of input: text (ingredients lists), images (dish photos), and audio (voice instructions). The system uses Google's Gemini AI to create comprehensive, detailed recipes tailored to your specific inputs.

## Features

### 🧠 LLM Integration
- **Google Gemini AI**: Advanced language model generates detailed, personalized recipes
- **Multimodal Processing**: Combines text, image, and audio inputs intelligently
- **Context-Aware Generation**: Considers all inputs to create cohesive recipes

### 📝 Text Input Processing
- **Ingredients Lists**: Parse structured ingredient lists with quantities
- **Recipe Descriptions**: Understand cooking preferences and dietary requirements
- **Cuisine Detection**: Automatically identify cuisine types from text

### 📸 Image Analysis
- **Dish Recognition**: Identify food dishes from uploaded photos
- **Cuisine Classification**: Determine cuisine type from visual cues
- **Confidence Scoring**: Assess accuracy of image classification

### 🎤 Audio Processing
- **Speech Recognition**: Convert voice instructions to text
- **Cooking Method Detection**: Extract cooking techniques from audio
- **Natural Language Processing**: Understand spoken cooking preferences

### 🍳 Recipe Generation
- **Complete Recipes**: Generate ingredients, instructions, timing, and tips
- **Nutritional Information**: Highlight key nutritional benefits
- **Recipe Variations**: Suggest alternative ingredients and methods
- **Difficulty Assessment**: Automatic difficulty level assignment

## Technology Stack

### Backend
- **Flask**: Web framework for API endpoints
- **Google Generative AI**: Gemini 1.5 Flash model for recipe generation
- **TensorFlow**: Image classification and processing
- **SpeechRecognition**: Audio transcription
- **NLTK**: Natural language processing
- **PyDub**: Audio processing

### Frontend
- **React**: Modern web interface
- **Tailwind CSS**: Responsive styling (via CDN)
- **Lucide React**: Icon components
- **Web Audio API**: Audio recording functionality

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ (for React frontend)
- Git

### Quick Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd flavorcraft
```

2. **Run the setup script**
```bash
python setup.py
```

This will automatically:
- Install system dependencies
- Set up Python environment
- Configure Google AI API
- Download required models
- Set up frontend dependencies

### Manual Setup

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Set up environment variables**
Create a `.env` file with:
```env
GOOGLE_API_KEY=AIzaSyDDhOVdFG5tl29-v1gi7KUqul7iPAX8oqc
FLASK_ENV=development
PORT=5000
```

## Usage

### Starting the Application

1. **Start the backend server**
```bash
python app.py
```
The API will run on `http://localhost:5007`

2. **Start the frontend (in a new terminal)**
```bash
npm start
```
The web app will open on `http://localhost:3000`

### Using FlavorCraft

1. **Text Input**: Enter ingredients lists or describe what you want to cook
2. **Image Upload**: Upload a photo of a dish you want to recreate
3. **Voice Recording**: Record cooking instructions or preferences
4. **Generate Recipe**: Click "Generate Recipe with AI" to create your personalized recipe

### API Endpoints

- `GET /` - Health check and system status
- `POST /predict` - Main recipe generation endpoint
- `POST /analyze-text` - Text-only analysis
- `POST /analyze-image` - Image-only analysis
- `POST /analyze-audio` - Audio-only analysis
- `POST /generate-recipe-llm` - Direct LLM recipe generation

## File Structure

```
flavorcraft/
├── app.py                 # Main Flask application with LLM integration
├── text_model.py          # Text processing and analysis
├── image_model.py         # Image classification model
├── audio_model.py         # Audio processing and transcription
├── requirements.txt       # Python dependencies
├── setup.py              # Installation script
├── package.json          # React frontend dependencies
├── App.js                # Main React component
├── App.css               # Styling
├── index.js              # React entry point
├── .env                  # Environment configuration
└── README.md             # This file
```

## Configuration

### Environment Variables

```env
# Google AI Configuration
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Flask Configuration
FLASK_ENV=development
PORT=5000
DEBUG=True

# File Upload
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=temp

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/flavorcraft.log
```

### Model Configuration

The application supports multiple AI models:
- **Primary**: Google Gemini 1.5 Flash (for recipe generation)
- **Image**: ResNet50/VGG16 (for dish classification)
- **Audio**: Google Speech Recognition + Sphinx (fallback)
- **Text**: NLTK + custom processing

## Development

### Adding New Features

1. **Backend Changes**: Modify `app.py` and related model files
2. **Frontend Changes**: Update `App.js` and components
3. **New Endpoints**: Add routes in `app.py`
4. **Model Updates**: Enhance processing in model files

### Testing

```bash
# Test backend
python -m pytest tests/

# Test API endpoints
curl http://localhost:5000/

# Test frontend
npm test
```

### Debugging

- Backend logs: Check console output when running `python app.py`
- Frontend logs: Open browser developer tools
- API testing: Use tools like Postman or curl
- Model issues: Check individual model imports in Python

## Troubleshooting

### Common Issues

1. **Google AI API Error**
   - Verify API key is correct
   - Check internet connection
   - Ensure API quotas are not exceeded

2. **Audio Recording Not Working**
   - Check microphone permissions
   - Verify HTTPS connection (required for audio)
   - Install audio dependencies: `pip install pyaudio`

3. **Image Classification Fails**
   - Install TensorFlow: `pip install tensorflow`
   - Verify image file format (JPG, PNG supported)
   - Check image file size (max 16MB)

4. **Speech Recognition Issues**
   - Install system dependencies: `sudo apt-get install portaudio19-dev`
   - Try different audio formats
   - Check microphone input levels

5. **Frontend Build Errors**
   - Ensure Node.js 16+ is installed
   - Clear npm cache: `npm cache clean --force`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

### Error Messages

- **"LLM model not available"**: Check Google AI API key configuration
- **"Audio model not available"**: Install speech recognition dependencies
- **"Image model not available"**: Install TensorFlow and related packages
- **"CORS error"**: Ensure backend is running on port 5000

## API Key Security

The Google AI API key is currently hardcoded for development purposes. For production:

1. Store in environment variables
2. Use secure configuration management
3. Implement rate limiting
4. Add API key rotation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone <your-fork-url>
cd flavorcraft

# Install dependencies
python setup.py

# Create development branch
git checkout -b feature/your-feature-name

# Make changes and test
python app.py  # Backend
npm start      # Frontend

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check this README
2. Review error logs
3. Test individual components
4. Check API quotas and keys

## Acknowledgments

- Google Generative AI for LLM capabilities
- TensorFlow team for image processing models
- React community for frontend framework
- Open source contributors for various libraries

## Version History

- **v1.0**: Initial release with LLM integration
- **v1.1**: Enhanced multimodal processing
- **v1.2**: Improved error handling and fallbacks
- **Current**: Production-ready with comprehensive features