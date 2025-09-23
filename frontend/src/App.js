import React, { useState, useRef, useEffect } from 'react';
import { ChefHat, Mic, MicOff, Camera, Sparkles, Clock, Users, Star, CheckCircle, AlertCircle, ImageIcon, Utensils } from 'lucide-react';
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
  const [generationInfo, setGenerationInfo] = useState(null);
  const [error, setError] = useState(null);

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
      setError("Unable to access microphone. Please check permissions.");
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
      const res = await fetch("http://localhost:5007/transcribe", { 
        method: "POST", 
        body: formData 
      });
      const data = await res.json();
      if (data.success) {
        setAudioTranscript(data.transcript || "");
      } else {
        setAudioTranscript("Error processing audio");
        console.error("Audio transcription failed:", data.error);
      }
    } catch (err) {
      console.error("Error transcribing audio:", err);
      setAudioTranscript("Error processing audio");
    }
  };

  // Determine if recipe is vegetarian based on ingredients
  const determineVegStatus = (ingredients) => {
    if (!ingredients || !Array.isArray(ingredients)) return 'veg';
    
    const nonVegKeywords = ['chicken', 'beef', 'pork', 'lamb', 'fish', 'salmon', 'shrimp', 'meat', 'turkey', 'duck', 'bacon'];
    const ingredientText = ingredients.join(' ').toLowerCase();
    
    for (const keyword of nonVegKeywords) {
      if (ingredientText.includes(keyword)) {
        return 'non-veg';
      }
    }
    return 'veg';
  };

  // Create fallback recipe when backend fails or provides incomplete data
  const createFallbackRecipe = (data = null) => {
    console.log("Creating fallback recipe with data:", data);
    
    return {
      name: "Custom Recipe",
      cuisine: "International",
      difficulty: "Medium",
      prepTime: "15 minutes",
      cookTime: "25 minutes",
      totalTime: "40 minutes",
      servings: 4,
      image: dishImage || "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop",
      description: "A delicious custom recipe based on your preferences",
      ingredients: [
        "2 tablespoons olive oil",
        "1 large onion, chopped",
        "3 cloves garlic, minced",
        "Your preferred main ingredients",
        "Salt and pepper to taste"
      ],
      instructions: [
        "Heat olive oil in a large pan over medium heat",
        "Add chopped onion and cook until softened",
        "Add garlic and cook for 1 minute",
        "Add your main ingredients and cook until done",
        "Season with salt and pepper and serve hot"
      ],
      tags: ["custom", "home-cooked"],
      tips: ["Adjust seasoning to taste", "Use fresh ingredients when possible"],
      cookingMethods: ["sauté"],
      nutritionalHighlights: ["Customizable to dietary needs"],
      variations: ["Add your favorite spices", "Substitute ingredients as needed"],
      vegStatus: "veg",
      
      // Analysis metadata
      imageClass: "Unknown",
      imageCuisine: "International", 
      imageConfidence: 0,
      audioTranscript: audioTranscript || "",
      hasTextInput: Boolean(recipeText),
      hasImageInput: Boolean(dishImage),
      hasAudioInput: Boolean(audioBlob),
      generationMethod: "fallback"
    };
  };

  // Generate recipe with enhanced error handling
  const generateRecipe = async () => {
    if (!recipeText && !dishImage && !audioBlob) {
      setError("Please provide at least one input to generate your recipe");
      return;
    }

    setIsProcessing(true);
    setError(null);
    setAnalysisResults(null);
    setGenerationInfo(null);

    const formData = new FormData();
    if (recipeText) formData.append("text", recipeText);
    if (dishImage) formData.append("image", dataURLtoFile(dishImage, "dish.png"));
    if (audioBlob) formData.append("audio", audioBlob, "voice.wav");

    try {
      const res = await fetch("http://localhost:5007/predict", { 
        method: "POST", 
        body: formData 
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();
      console.log("Backend response:", data);

      if (data.success && data.recipe) {
        // Process the backend response properly
        const backendRecipe = data.recipe;
        
        // Map backend recipe fields to frontend expected fields
        const processedRecipe = {
          // Basic info - handle both naming conventions
          name: backendRecipe.recipe_name || backendRecipe.name || "Generated Recipe",
          cuisine: backendRecipe.cuisine_type || backendRecipe.cuisine || "International",
          difficulty: backendRecipe.difficulty_level || backendRecipe.difficulty || "Medium",
          prepTime: backendRecipe.prep_time || backendRecipe.prepTime || "15 minutes",
          cookTime: backendRecipe.cook_time || backendRecipe.cookTime || "25 minutes", 
          totalTime: backendRecipe.total_time || backendRecipe.totalTime || "40 minutes",
          servings: backendRecipe.servings || 4,
          image: dishImage || "https://images.unsplash.com/photo-1588166524941-3bf61a9c41db?w=400&h=300&fit=crop",
          description: backendRecipe.description || "A delicious recipe generated based on your inputs",
          
          // Recipe content
          ingredients: Array.isArray(backendRecipe.ingredients) ? backendRecipe.ingredients : ["Ingredients will be generated based on your inputs"],
          instructions: Array.isArray(backendRecipe.instructions) ? backendRecipe.instructions : ["Instructions will be provided"],
          
          // Additional content - provide defaults if missing
          tags: Array.isArray(backendRecipe.tags) ? backendRecipe.tags : ["homemade"],
          tips: Array.isArray(backendRecipe.tips) ? backendRecipe.tips : ["Enjoy your meal!"],
          cookingMethods: Array.isArray(backendRecipe.cooking_methods) ? backendRecipe.cooking_methods : [],
          nutritionalHighlights: Array.isArray(backendRecipe.nutritional_highlights) ? backendRecipe.nutritional_highlights : [],
          variations: Array.isArray(backendRecipe.variations) ? backendRecipe.variations : [],
          
          // Classification info
          vegStatus: determineVegStatus(backendRecipe.ingredients),
          
          // Analysis metadata
          imageClass: data.image_class || data.classification_details?.dish || "Unknown",
          imageCuisine: data.classification_details?.cuisine || "Unknown",
          imageConfidence: data.classification_details?.confidence || 0,
          audioTranscript: data.audio_transcript || audioTranscript || "",
          hasTextInput: Boolean(recipeText),
          hasImageInput: Boolean(dishImage),
          hasAudioInput: Boolean(audioBlob),
          generationMethod: data.generation_info?.method || "api"
        };

        // Set analysis results if available
        if (data.analysis_results) {
          setAnalysisResults(data.analysis_results);
        }
        
        if (data.generation_info) {
          setGenerationInfo(data.generation_info);
        }

        setGeneratedRecipe(processedRecipe);
        console.log("Processed recipe:", processedRecipe);
        
      } else {
        console.error("Backend returned unsuccessful response:", data);
        setError(data.error || "Recipe generation failed");
        setGeneratedRecipe(createFallbackRecipe(data));
      }
    } catch (err) {
      console.error("Error generating recipe:", err);
      setError(`Connection error: ${err.message}`);
      
      // Use fallback recipe on network/server errors
      setGeneratedRecipe(createFallbackRecipe());
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
    setGenerationInfo(null);
    setRecordingTime(0);
    setError(null);
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

  const VegNonVegBadge = ({ vegStatus }) => {
    if (vegStatus === 'veg') {
      return (
        <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center veg-badge">
          <div className="w-2 h-2 bg-white rounded-full mr-1"></div>
          VEG
        </div>
      );
    } else {
      return (
        <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center non-veg-badge">
          <div className="w-2 h-2 bg-white rounded-full mr-1"></div>
          NON-VEG
        </div>
      );
    }
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
            <p className="text-gray-600 text-sm">Smart Recipe Curation Platform</p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {!generatedRecipe ? (
          <div className="bg-white rounded-2xl shadow-xl p-6 space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center justify-center">
                <Sparkles className="mr-2 text-orange-500" />
                Curate Your Recipe
              </h2>
              <p className="text-gray-600">Share your ingredients, upload a dish photo, or record your preferences to get a personalized recipe</p>
            </div>

            {/* Text Input */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Ingredients Available at Your Home
              </label>
              <textarea
                placeholder="List the ingredients you have available at home...

Examples:
• 2 lbs chicken breast
• 1 onion, chopped  
• 3 cloves garlic
• coconut milk
• curry powder
• turmeric

Or describe what you want to cook: 'spicy chicken curry for dinner' or 'quick pasta meal for 4 people'"
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none enhanced-input"
                rows="7"
                value={recipeText}
                onChange={(e) => setRecipeText(e.target.value)}
              />
              {recipeText && (
                <div className="text-xs text-gray-500 flex items-center space-x-2">
                  <span>{recipeText.length} characters</span>
                  <span>•</span>
                  <span>Recipe will be curated based on your available ingredients</span>
                </div>
              )}
            </div>

            {/* Image Input */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Reference Picture</label>
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
                  className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors interactive-button"
                >
                  <Camera className="h-4 w-4" />
                  <span>Upload Reference Image</span>
                </button>
                {dishImage && (
                  <span className="text-green-600 text-sm flex items-center space-x-1">
                    <CheckCircle className="h-4 w-4" />
                    <span>Image uploaded - will help identify dish and cooking style</span>
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500">Upload a photo of the dish you want to make or a similar recipe for reference</p>
            </div>

            {dishImage && (
              <div className="mt-4">
                <img src={dishImage} alt="Reference Dish" className="w-full max-w-md mx-auto rounded-lg shadow-md" />
                <p className="text-center text-sm text-gray-500 mt-2 flex items-center justify-center space-x-1">
                  <ImageIcon className="h-3 w-3" />
                  <span>This reference image will help create a similar recipe</span>
                </p>
              </div>
            )}

            {/* Audio Input */}
            <div className="space-y-4">
              <label className="block text-sm font-medium text-gray-700">Do you have any instructions for me?</label>
              <div className="flex items-center space-x-4">
                {!isRecording ? (
                  <button 
                    onClick={startRecording} 
                    className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg transition-colors interactive-button"
                  >
                    <Mic className="h-4 w-4" />
                    <span>Start Recording</span>
                  </button>
                ) : (
                  <button 
                    onClick={stopRecording} 
                    className="flex items-center space-x-2 bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors recording-pulse"
                  >
                    <MicOff className="h-4 w-4" />
                    <span>Stop Recording ({formatTime(recordingTime)})</span>
                  </button>
                )}
                {audioBlob && (
                  <span className="text-green-600 text-sm flex items-center space-x-1">
                    <CheckCircle className="h-4 w-4" />
                    <span>Instructions recorded and will be incorporated</span>
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500">Share any specific preferences like "make it for 4 people", "mild spice level", or "30-minute cooking time"</p>

              {isRecording && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 recording-indicator">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-red-700 text-sm font-medium">Recording... {formatTime(recordingTime)}</span>
                  </div>
                  <p className="text-red-600 text-xs mt-1">Tell me about serving size, spice level, cooking time, or dietary preferences</p>
                </div>
              )}

              {audioTranscript && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-blue-800 text-sm">
                    <strong>Your Instructions:</strong> {audioTranscript}
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 pt-4">
              <button
                onClick={generateRecipe}
                className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 px-6 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center interactive-button"
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <span className="flex items-center justify-center">
                    <div className="loading-spinner mr-2"></div>
                    Curating your recipe...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Utensils className="mr-2 h-5 w-5" />
                    Generate Your Curated Recipe
                  </span>
                )}
              </button>

              <button 
                onClick={resetForm} 
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors interactive-button"
              >
                Reset
              </button>
            </div>

            {/* Input Summary */}
            {(recipeText || dishImage || audioBlob) && (
              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 info-card">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Recipe Inputs:</h4>
                <div className="space-y-1 text-sm text-gray-600">
                  {recipeText && <div>✓ Ingredients: Available ingredients and preferences provided</div>}
                  {dishImage && <div>✓ Reference: Dish photo uploaded for style guidance</div>}
                  {audioBlob && <div>✓ Instructions: Voice preferences recorded</div>}
                  <div className="text-xs text-orange-600 mt-2">
                    Your personalized recipe will be curated based on these inputs
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* Enhanced Recipe Display */
          <div className="space-y-6">
            {/* Recipe Header */}
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden recipe-card">
              <div className="relative">
                <img 
                  src={generatedRecipe.image} 
                  alt={generatedRecipe.name}
                  className="w-full h-64 object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
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
                
                {/* Veg/Non-Veg Badge */}
                <VegNonVegBadge vegStatus={generatedRecipe.vegStatus} />
              </div>
              
              <div className="p-6">
                <p className="text-gray-700 text-lg leading-relaxed mb-4">{generatedRecipe.description}</p>
                
                {/* Tags */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {generatedRecipe.tags && generatedRecipe.tags.map((tag, index) => (
                    <span key={index} className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm tag">
                      {tag}
                    </span>
                  ))}
                  {generatedRecipe.cookingMethods && generatedRecipe.cookingMethods.map((method, index) => (
                    <span key={`method-${index}`} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm tag">
                      {method}
                    </span>
                  ))}
                </div>

                {/* Image Classification Results */}
                {generatedRecipe.hasImageInput && generatedRecipe.imageClass !== 'Unknown' && (
                  <div className="bg-green-50 rounded-lg p-4 mb-4 border border-green-200 info-card">
                    <h4 className="font-semibold mb-3 text-green-800 flex items-center">
                      <Camera className="mr-2 h-4 w-4" />
                      Image Analysis Results
                    </h4>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-green-600">Identified Dish:</span>
                          <span className="font-medium text-green-800">{generatedRecipe.imageClass}</span>
                        </div>
                        
                        {generatedRecipe.imageCuisine && generatedRecipe.imageCuisine !== 'Unknown' && (
                          <div className="flex items-center justify-between">
                            <span className="text-green-600">Detected Cuisine:</span>
                            <span className="font-medium text-green-800">{generatedRecipe.imageCuisine}</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="space-y-2">
                        {generatedRecipe.imageConfidence > 0 && (
                          <div className="flex items-center justify-between">
                            <span className="text-green-600">Confidence Score:</span>
                            <span className={`font-medium ${getConfidenceColor(generatedRecipe.imageConfidence)}`}>
                              {(generatedRecipe.imageConfidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                        
                        {generatedRecipe.audioTranscript && (
                          <p><strong>Voice Instructions:</strong> "{generatedRecipe.audioTranscript.slice(0, 40)}..."</p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Timing Information */}
            <div className="bg-white rounded-2xl shadow-xl p-6 info-card">
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
              <div className="bg-white rounded-2xl shadow-xl p-6 recipe-card">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Ingredients</h2>
                <ul className="space-y-3">
                  {generatedRecipe.ingredients.map((ingredient, index) => (
                    <li key={index} className="flex items-start ingredient-item">
                      <span className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                      <span className="text-gray-700">{ingredient}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Instructions */}
              <div className="bg-white rounded-2xl shadow-xl p-6 recipe-card">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Instructions</h2>
                <ol className="space-y-4">
                  {generatedRecipe.instructions.map((step, index) => (
                    <li key={index} className="flex items-start instruction-step">
                      <span className="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 flex-shrink-0 mt-0.5 step-counter">
                        {index + 1}
                      </span>
                      <span className="text-gray-700 leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>

            {/* Additional Content */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Tips */}
              {generatedRecipe.tips && generatedRecipe.tips.length > 0 && (
                <div className="bg-green-50 rounded-2xl p-6 border border-green-200 info-card">
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

              {/* Nutritional Highlights */}
              {generatedRecipe.nutritionalHighlights && generatedRecipe.nutritionalHighlights.length > 0 && (
                <div className="bg-blue-50 rounded-2xl p-6 border border-blue-200 info-card">
                  <h3 className="text-lg font-bold text-blue-800 mb-3">
                    Nutritional Highlights
                  </h3>
                  <ul className="space-y-2">
                    {generatedRecipe.nutritionalHighlights.map((highlight, index) => (
                      <li key={index} className="text-blue-700">• {highlight}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Variations */}
            {generatedRecipe.variations && generatedRecipe.variations.length > 0 && (
              <div className="bg-yellow-50 rounded-2xl p-6 border border-yellow-200 info-card">
                <h3 className="text-lg font-bold text-yellow-800 mb-3">
                  Recipe Variations
                </h3>
                <ul className="space-y-2">
                  {generatedRecipe.variations.map((variation, index) => (
                    <li key={index} className="text-yellow-700">• {variation}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Generation Info */}
            {generationInfo && (
              <div className="bg-gray-50 rounded-2xl p-6 border border-gray-200 info-card">
                <h3 className="text-lg font-bold text-gray-800 mb-3">Generation Details</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
                  <div>
                    <p><strong>Method:</strong> {generationInfo.method || generatedRecipe.generationMethod}</p>
                    <p><strong>Processing Time:</strong> {generationInfo.processing_time || 'N/A'}s</p>
                  </div>
                  <div>
                    <p><strong>Inputs Used:</strong></p>
                    <ul className="mt-1 space-y-1">
                      {generatedRecipe.hasTextInput && <li>✓ Text ingredients</li>}
                      {generatedRecipe.hasImageInput && <li>✓ Reference image</li>}
                      {generatedRecipe.hasAudioInput && <li>✓ Voice instructions</li>}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Back Button */}
            <div className="text-center">
              <button 
                onClick={resetForm} 
                className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-8 py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all flex items-center mx-auto interactive-button"
              >
                <Utensils className="mr-2 h-5 w-5" />
                Curate Another Recipe
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlavorCraft;