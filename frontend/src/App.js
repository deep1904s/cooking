import React, { useState, useRef, useEffect } from 'react';
import { ChefHat, Mic, MicOff, Camera, Sparkles, Clock, Users, Star } from 'lucide-react';
import './App.css';

const FlavorCraft = () => {
  const [recipeText, setRecipeText] = useState('');
  const [dishImage, setDishImage] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioTranscript, setAudioTranscript] = useState('');
  const [generatedRecipe, setGeneratedRecipe] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [analysisResults, setAnalysisResults] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioStreamRef = useRef(null);
  const timerRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Audio recording functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const chunks = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
        await transcribeAudio(blob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      timerRef.current = setInterval(() => setRecordingTime(prev => prev + 1), 1000);

    } catch (err) {
      console.error("Microphone access error:", err);
      alert("Unable to access microphone. Check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Image handling
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => setDishImage(event.target.result);
      reader.readAsDataURL(file);
    }
  };

  const dataURLtoFile = (dataurl, filename) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    const u8arr = new Uint8Array(bstr.length);
    for (let i = 0; i < bstr.length; i++) u8arr[i] = bstr.charCodeAt(i);
    return new File([u8arr], filename, { type: mime });
  };

  // Transcribe audio via backend
  const transcribeAudio = async (blob) => {
    if (!blob) return;
    const formData = new FormData();
    formData.append("audio", blob, "voice.wav");

    try {
      const res = await fetch("http://localhost:5005/analyze-audio", { 
        method: "POST", 
        body: formData 
      });
      const data = await res.json();
      setAudioTranscript(data.transcript || "");
    } catch (err) {
      console.error("Error transcribing audio:", err);
      setAudioTranscript("Error processing audio");
    }
  };

  // Generate recipe with enhanced processing
  const generateRecipe = async () => {
    if (!recipeText && !dishImage && !audioBlob) {
      alert("Provide at least one input (text, image, or audio)");
      return;
    }

    setIsProcessing(true);
    setAnalysisResults(null);

    const formData = new FormData();
    if (recipeText) formData.append("text", recipeText);
    if (dishImage) formData.append("image", dataURLtoFile(dishImage, "dish.png"));
    if (audioBlob) formData.append("audio", audioBlob, "voice.wav");

    try {
      const res = await fetch("http://localhost:5005/predict", { 
        method: "POST", 
        body: formData 
      });
      const data = await res.json();

      if (data.success) {
        const recipe = data.recipe;
        setAnalysisResults(data.analysis_results);
        
        setGeneratedRecipe({
          name: recipe.name || "Generated Recipe",
          cuisine: recipe.cuisine || "International",
          difficulty: recipe.difficulty || "Medium",
          prepTime: recipe.prep_time || "15 minutes",
          cookTime: recipe.cook_time || "25 minutes",
          totalTime: recipe.total_time || "40 minutes",
          servings: recipe.servings || 4,
          image: dishImage || "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop",
          description: recipe.description || "A delicious recipe generated from your inputs",
          ingredients: recipe.ingredients || ["Ingredients will be listed here"],
          instructions: recipe.instructions || ["Instructions will be provided here"],
          tags: recipe.tags || ["homemade"],
          tips: recipe.tips || ["Enjoy your meal!"],
          cookingMethods: recipe.cooking_methods || [],
          
          // Analysis metadata
          imageClass: data.analysis_results?.image?.food_class || "Unknown",
          imageCuisine: data.analysis_results?.image?.cuisine || "Unknown",
          imageConfidence: data.analysis_results?.image?.confidence || 0,
          audioTranscript: audioTranscript || data.audio_transcript || "",
          hasTextInput: Boolean(recipeText),
          hasImageInput: Boolean(dishImage),
          hasAudioInput: Boolean(audioBlob),
          generationMethod: recipe.analysis_metadata?.generation_method || "enhanced"
        });
      } else {
        alert("Error generating recipe: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      console.error("Error generating recipe:", err);
      alert("Error connecting to server. Make sure the backend is running on port 5005.");
      
      // Enhanced fallback demo recipe
      setGeneratedRecipe({
        name: "Demo Recipe (Backend Not Connected)",
        cuisine: "International",
        difficulty: "Medium",
        prepTime: "15 minutes",
        cookTime: "25 minutes", 
        totalTime: "40 minutes",
        servings: 4,
        image: dishImage || "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop",
        description: "A delicious recipe (demo mode - connect backend for full functionality)",
        ingredients: [
          "2 tablespoons olive oil",
          "1 large onion, chopped",
          "3 cloves garlic, minced",
          "1 lb main protein or vegetables",
          "Salt and pepper to taste",
          "Fresh herbs for garnish"
        ],
        instructions: [
          "Heat olive oil in a large pan over medium heat",
          "Add chopped onion and cook until softened, about 5 minutes",
          "Add minced garlic and cook for 1 minute until fragrant",
          "Add your main ingredients and cook until done",
          "Season with salt and pepper to taste",
          "Garnish with fresh herbs and serve hot"
        ],
        tags: ["demo", "easy", "homemade"],
        tips: ["This is a demo recipe - connect the backend for AI-generated recipes!"],
        cookingMethods: ["sauté"],
        
        imageClass: dishImage ? "Food dish" : "No image",
        imageCuisine: "Unknown",
        imageConfidence: 0,
        audioTranscript: audioTranscript || "No audio processed",
        hasTextInput: Boolean(recipeText),
        hasImageInput: Boolean(dishImage),
        hasAudioInput: Boolean(audioBlob),
        generationMethod: "demo"
      });
    }

    setIsProcessing(false);
  };

  const resetForm = () => {
    setRecipeText('');
    setDishImage(null);
    setAudioBlob(null);
    setAudioTranscript('');
    setGeneratedRecipe(null);
    setAnalysisResults(null);
    setRecordingTime(0);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-yellow-600 bg-yellow-100';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence > 0.7) return 'text-green-600';
    if (confidence > 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-orange-100">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center space-x-3">
          <div className="bg-gradient-to-r from-orange-500 to-red-500 p-2 rounded-xl">
            <ChefHat className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
              FlavorCraft
            </h1>
            <p className="text-gray-600 text-sm">AI-Powered Multimodal Recipe Generator</p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {!generatedRecipe ? (
          <div className="bg-white rounded-2xl shadow-xl p-6 space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center justify-center">
                <Sparkles className="mr-2 text-orange-500" />
                Create Your Recipe
              </h2>
              <p className="text-gray-600">Enter ingredients, upload a dish photo, or record cooking instructions to generate a detailed recipe</p>
            </div>

            {/* Text Input */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Recipe Text, Ingredients List, or Cooking Instructions
              </label>
              <textarea
                placeholder="Enter ingredients list, describe what you want to cook, or provide cooking instructions...
Example: 
- 2 lbs chicken breast
- 1 onion, chopped  
- 3 cloves garlic
- coconut milk
- curry powder
- turmeric

I want to make a curry..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none"
                rows="6"
                value={recipeText}
                onChange={(e) => setRecipeText(e.target.value)}
              />
              {recipeText && (
                <div className="text-xs text-gray-500">
                  {recipeText.length} characters • The AI will analyze your text for ingredients, cooking methods, and cuisine
                </div>
              )}
            </div>

            {/* Image Input */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Upload Dish Image</label>
              <div className="flex items-center space-x-4">
                <input 
                  ref={fileInputRef}
                  type="file" 
                  accept="image/*" 
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Camera className="h-4 w-4" />
                  <span>Choose Image</span>
                </button>
                {dishImage && <span className="text-green-600 text-sm">✓ Image uploaded - AI will identify the dish and cuisine</span>}
              </div>
            </div>

            {dishImage && (
              <div className="mt-4">
                <img src={dishImage} alt="Dish Preview" className="w-full max-w-md mx-auto rounded-lg shadow-md" />
                <p className="text-center text-sm text-gray-500 mt-2">AI will analyze this image to identify the dish type and suggest appropriate ingredients</p>
              </div>
            )}

            {/* Audio Input */}
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">Voice Instructions</label>
              <div className="flex items-center space-x-4">
                {!isRecording ? (
                  <button 
                    onClick={startRecording} 
                    className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-colors"
                  >
                    <Mic className="h-4 w-4" />
                    <span>Start Recording</span>
                  </button>
                ) : (
                  <button 
                    onClick={stopRecording} 
                    className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors"
                  >
                    <MicOff className="h-4 w-4" />
                    <span>Stop Recording ({formatTime(recordingTime)})</span>
                  </button>
                )}
                {audioBlob && <span className="text-green-600 text-sm">✓ Audio recorded - AI will transcribe and analyze your instructions</span>}
              </div>

              {isRecording && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-red-700 text-sm font-medium">Recording... {formatTime(recordingTime)}</span>
                  </div>
                  <p className="text-red-600 text-xs mt-1">Speak your cooking instructions, ingredient list, or describe what you want to make</p>
                </div>
              )}

              {audioTranscript && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-blue-800 text-sm"><strong>Transcript:</strong> {audioTranscript}</p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 pt-4">
              <button
                onClick={generateRecipe}
                className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 px-6 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <span className="flex items-center justify-center">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Analyzing & Generating Recipe...
                  </span>
                ) : (
                  "Generate Recipe with AI"
                )}
              </button>

              <button 
                onClick={resetForm} 
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Reset
              </button>
            </div>
          </div>
        ) : (
          /* Enhanced Recipe Display */
          <div className="space-y-6">
            {/* Recipe Header with Analysis Info */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="relative">
                <img 
                  src={generatedRecipe.image} 
                  alt={generatedRecipe.name}
                  className="w-full h-64 object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
                <div className="absolute bottom-4 left-6 text-white">
                  <h1 className="text-3xl font-bold mb-2">{generatedRecipe.name}</h1>
                  <div className="flex items-center space-x-4 text-sm">
                    <span>{generatedRecipe.cuisine}</span>
                    <span>•</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getDifficultyColor(generatedRecipe.difficulty)}`}>
                      {generatedRecipe.difficulty}
                    </span>
                    <span>•</span>
                    <div className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      <span>{generatedRecipe.totalTime}</span>
                    </div>
                    <span>•</span>
                    <div className="flex items-center">
                      <Users className="h-3 w-3 mr-1" />
                      <span>{generatedRecipe.servings} servings</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="p-6">
                <p className="text-gray-700 text-lg leading-relaxed mb-4">{generatedRecipe.description}</p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {generatedRecipe.tags && generatedRecipe.tags.map((tag, index) => (
                    <span key={index} className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm">
                      {tag}
                    </span>
                  ))}
                  {generatedRecipe.cookingMethods && generatedRecipe.cookingMethods.map((method, index) => (
                    <span key={`method-${index}`} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                      {method}
                    </span>
                  ))}
                </div>

                {/* Enhanced Analysis Results */}
                <div className="bg-gray-50 rounded-lg p-4 text-sm">
                  <h4 className="font-semibold mb-3 text-gray-800">AI Analysis Results:</h4>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Input Sources:</span>
                        <div className="flex items-center space-x-2">
                          {generatedRecipe.hasTextInput && <span className="w-2 h-2 bg-green-500 rounded-full" title="Text input"></span>}
                          {generatedRecipe.hasImageInput && <span className="w-2 h-2 bg-blue-500 rounded-full" title="Image input"></span>}
                          {generatedRecipe.hasAudioInput && <span className="w-2 h-2 bg-purple-500 rounded-full" title="Audio input"></span>}
                        </div>
                      </div>
                      
                      {generatedRecipe.imageClass !== 'Unknown' && (
                        <p><strong>Image Classification:</strong> {generatedRecipe.imageClass}</p>
                      )}
                      
                      {generatedRecipe.imageConfidence > 0 && (
                        <p><strong>Classification Confidence:</strong> 
                          <span className={`ml-1 ${getConfidenceColor(generatedRecipe.imageConfidence)}`}>
                            {(generatedRecipe.imageConfidence * 100).toFixed(1)}%
                          </span>
                        </p>
                      )}
                      
                      {generatedRecipe.imageCuisine && generatedRecipe.imageCuisine !== 'Unknown' && (
                        <p><strong>Image-Detected Cuisine:</strong> {generatedRecipe.imageCuisine}</p>
                      )}
                    </div>
                    
                    <div className="space-y-2">
                      {generatedRecipe.audioTranscript && (
                        <p><strong>Audio Transcript:</strong> "{generatedRecipe.audioTranscript.slice(0, 60)}..."</p>
                      )}
                      
                      <p><strong>Generation Method:</strong> 
                        <span className={`ml-1 px-2 py-0.5 rounded text-xs ${
                          generatedRecipe.generationMethod === 'enhanced' ? 'bg-green-100 text-green-700' : 
                          generatedRecipe.generationMethod === 'demo' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {generatedRecipe.generationMethod}
                        </span>
                      </p>
                      
                      <p><strong>Recipe Complexity:</strong> {generatedRecipe.ingredients.length} ingredients, {generatedRecipe.instructions.length} steps</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Timing Information */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Cooking Timeline</h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Clock className="h-6 w-6 mx-auto mb-2 text-blue-600" />
                  <div className="text-sm text-gray-600">Prep Time</div>
                  <div className="font-semibold text-blue-700">{generatedRecipe.prepTime}</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <Clock className="h-6 w-6 mx-auto mb-2 text-orange-600" />
                  <div className="text-sm text-gray-600">Cook Time</div>
                  <div className="font-semibold text-orange-700">{generatedRecipe.cookTime}</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Clock className="h-6 w-6 mx-auto mb-2 text-green-600" />
                  <div className="text-sm text-gray-600">Total Time</div>
                  <div className="font-semibold text-green-700">{generatedRecipe.totalTime}</div>
                </div>
              </div>
            </div>

            {/* Ingredients and Instructions */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Ingredients */}
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Ingredients</h2>
                <ul className="space-y-3">
                  {generatedRecipe.ingredients.map((ingredient, index) => (
                    <li key={index} className="flex items-start">
                      <span className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                      <span className="text-gray-700">{ingredient}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Instructions */}
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Instructions</h2>
                <ol className="space-y-4">
                  {generatedRecipe.instructions.map((step, index) => (
                    <li key={index} className="flex items-start">
                      <span className="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0 mt-0.5">
                        {index + 1}
                      </span>
                      <span className="text-gray-700 leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>

            {/* Tips */}
            {generatedRecipe.tips && generatedRecipe.tips.length > 0 && (
              <div className="bg-green-50 rounded-2xl p-6 border border-green-200">
                <h3 className="text-lg font-bold text-green-800 mb-3 flex items-center">
                  <Star className="mr-2" />
                  Chef's Tips
                </h3>
                <ul className="space-y-2">
                  {generatedRecipe.tips.map((tip, index) => (
                    <li key={index} className="text-green-700">• {tip}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Back Button */}
            <div className="text-center">
              <button 
                onClick={resetForm} 
                className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-8 py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all"
              >
                Generate Another Recipe
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlavorCraft;