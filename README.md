# FlavorCraft - Multimodal Recipe Generator

A sophisticated AI-powered application that generates detailed recipes from multiple input types: text descriptions, dish images, and voice instructions.

## 🌟 Features

### Multimodal Input Processing
- **Text Analysis**: Extract ingredients, cooking methods, and cuisine type from recipe text
- **Image Classification**: Identify dishes and cuisine from food photos using deep learning
- **Audio Transcription**: Convert voice instructions to text and extract cooking keywords

### Comprehensive Recipe Generation
- Detailed ingredient lists with quantities
- Step-by-step cooking instructions
- Cuisine classification and cultural context
- Cooking time estimates and difficulty levels
- Professional cooking tips and techniques
- Nutritional insights and recommendations

### Modern User Interface
- Beautiful, responsive React frontend
- Intuitive tab-based input system
- Real-time audio recording with visual feedback
- Drag-and-drop image uploads
- Professional recipe presentation

## 🏗️ Architecture

```
FlavorCraft/
├── Frontend (React)
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styling
│   │   └── index.js        # Entry point
│   └── public/
│
├── Backend (Python/Flask)
│   ├── app.py              # Main Flask application
│   ├── audio_model.py      # Speech-to-text processing
│   ├── image_model.py      # Image classification
│   ├── text_model.py       # Text analysis and NLP
│   ├── requirements.txt    # Python dependencies
│   └── setup.py           # Automated setup script
│
└── Configuration
    ├── .env               # Environment variables
    └── README.md         # This file
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 14+**
- **npm or yarn**

### Automated Setup

1. **Clone the repository**
```bash
git clone <your-repository>
cd flavorcraft
```

2. **Run the automated setup**
```bash
python setup.py
```

This will:
- Install system dependencies
- Install Python packages
- Download required AI models
- Set up NLTK data
- Create necessary directories
- Configure environment variables

3. **Start the backend server**
```bash
python app.py
```

4. **Start the React frontend**
```bash
npm start
```

Visit `http://localhost:3000` to use the application!

### Manual Setup

If you prefer manual installation:

#### Backend Setup

1. **Create Python virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install system dependencies**

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev ffmpeg python3-dev build-essential
```

**macOS:**
```bash
brew install portaudio ffmpeg
```

**Windows:**
- Install Visual Studio Build Tools
- Install FFmpeg and add to PATH

4. **Download NLTK data**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

5. **Start the Flask server**
```bash
python app.py
```

#### Frontend Setup

1. **Install Node.js dependencies**
```bash
npm install
```

2. **Install additional dependencies**
```bash
npm install lucide-react
```

3. **Start the React development server**
```bash
npm start
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True
PORT=5000

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=temp

# Model Configuration
USE_GPU=True
MODEL_CACHE_DIR=models

# API Configuration
API_TIMEOUT=300
MAX_WORKERS=4
```

### Model Configuration

The application uses several AI models:

- **Image Classification**: ResNet50/VGG16 (pre-trained on ImageNet)
- **Speech Recognition**: Google Web Speech API with Sphinx fallback
- **Text Processing**: NLTK with custom recipe analysis

## 📡 API Endpoints

### Main Endpoints

- `POST /predict` - Multimodal recipe generation
- `POST /analyze-text` - Text-only analysis
- `POST /analyze-image` - Image-only analysis  
- `POST /analyze-audio` - Audio-only analysis
- `GET /` - Health check

### Request Format

**Multimodal Request:**
```javascript
const formData = new FormData();
formData.append('text', 'Recipe description...');
formData.append('image', imageFile);
formData.append('audio', audioBlob, 'voice.wav');

fetch('http://localhost:5000/predict', {
  method: 'POST',
  body: formData
});
```

### Response Format

```json
{
  "success": true,
  "recipe": {
    "name": "Butter Chicken Masala",
    "cuisine": "Indian",
    "difficulty": "Medium",
    "servings": 4,
    "cook_time": "45 minutes",
    "ingredients": ["1 lb chicken", "1 cup cream", ...],
    "instructions": ["Heat oil...", "Add chicken...", ...],
    "tags": ["spicy", "creamy", "indian"],
    "tips": ["Marinate for better flavor", ...]
  },
  "analysis_results": {
    "text": {...},
    "image": {...},
    "audio": {...}
  }
}
```

## 🎯 Usage Examples

### Text Input
```
Butter Chicken Recipe

Ingredients:
- 2 lbs chicken breast, cubed
- 1 cup heavy cream
- 2 tbsp butter
- 1 onion, chopped
- 2 tsp garam masala

Instructions:
1. Marinate chicken for 30 minutes
2. Cook chicken until golden
3. Sauté onions until soft
4. Add spices and simmer
```

### Image Input
- Upload photos of completed dishes
- Support for: JPG, PNG, GIF, WebP
- Automatic cuisine classification
- Ingredient suggestion based on visual analysis

### Audio Input
- Record cooking instructions or descriptions
- Automatic transcription to text
- Keyword extraction for cooking methods
- Support for multiple audio formats

## 🧪 Testing

Run the test suite:

```bash
# Backend tests
python -m pytest

# Frontend tests
npm test
```

## 🔍 Troubleshooting

### Common Issues

**1. Audio recording not working**
- Check browser microphone permissions
- Ensure HTTPS in production (required for microphone access)
- Verify pyaudio installation

**2. Image classification fails**
- Ensure TensorFlow is properly installed
- Check if GPU drivers are up to date (for GPU acceleration)
- Verify image file formats are supported

**3. Backend connection errors**
- Ensure Flask server is running on port 5000
- Check CORS configuration
- Verify firewall settings

**4. Model loading errors**
- Run `python setup.py` to download required models
- Check internet connection for model downloads
- Ensure sufficient disk space

### Performance Optimization

**For faster image processing:**
- Enable GPU acceleration (install tensorflow-gpu)
- Use SSD storage for model caching
- Optimize batch processing for multiple images

**For better audio quality:**
- Use higher quality audio input devices
- Ensure quiet environment for recording
- Consider noise cancellation preprocessing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Add tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **TensorFlow** for deep learning models
- **React** for the beautiful frontend
- **Flask** for the robust backend
- **NLTK** for natural language processing
- **SpeechRecognition** for audio processing
- **OpenAI** for inspiration and AI guidance

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🚀 Future Enhancements

- [ ] Support for more languages and cuisines
- [ ] Recipe rating and review system
- [ ] Meal planning and shopping list generation
- [ ] Integration with nutrition APIs
- [ ] Mobile app development
- [ ] Social sharing features
- [ ] Advanced dietary restriction handling
- [ ] Video input support
- [ ] Real-time collaboration features