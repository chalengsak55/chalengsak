# 🎤 Argue with AI Avatar - TikTok-Style Debate Game MVP

A full-stack MVP where users record voice arguments and receive TikTok-style reactions from an AI avatar named "Mina". Perfect for creating shareable, viral-ready debate content!

## 🌟 Features

- **🎙️ Browser Audio Recording**: Record arguments directly in the browser (no file uploads needed)
- **🤖 AI Transcription**: Powered by OpenAI Whisper API for accurate speech-to-text
- **🎯 Smart Scoring**: GPT-4 evaluates arguments with scores (1-10), emojis, and sassy comments
- **👩‍💻 AI Avatar Reactions**: Optional HeyGen-powered avatar videos with personalized reactions
- **📱 TikTok-Style UI**: Modern, mobile-friendly interface with viral-ready design
- **📊 Shareable Results**: Download and share your argument scores and feedback

## 🚀 Tech Stack

- **Frontend**: Streamlit + Custom HTML/CSS/JavaScript
- **Backend**: Python
- **APIs**: 
  - OpenAI Whisper (transcription)
  - OpenAI GPT-4 (scoring & feedback)
  - HeyGen API (avatar videos, optional)

## 📂 Project Structure

```
audio-recorder-mvp/
├── app.py                 # Main Streamlit application
├── scoring.py             # Main orchestration logic
├── whisper_transcribe.py  # Audio transcription module
├── gpt_feedback.py        # GPT-4 feedback generation
├── avatar_gen.py          # HeyGen avatar video generation
├── audio-recorder.html    # Browser audio recording interface
├── assets/               # Audio/video storage
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd audio-recorder-mvp
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Required: OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: HeyGen API Configuration (for avatar videos)
HEYGEN_API_KEY=your_heygen_api_key_here
HEYGEN_AVATAR_ID=your_avatar_id_here
```

### 4. Get API Keys

#### OpenAI API Key (Required)
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add it to your `.env` file

#### HeyGen API Key (Optional)
1. Sign up at [HeyGen](https://www.heygen.com/)
2. Get your API key from the dashboard
3. Choose an avatar ID from available avatars
4. Add both to your `.env` file

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎮 How to Use

### Method 1: Browser Recording
1. Click the "🎤 Record Audio" tab
2. Click the microphone button to start recording
3. Speak your argument clearly
4. Click stop when finished
5. Click "🚀 Analyze My Argument"

### Method 2: File Upload
1. Click the "📁 Upload File" tab
2. Upload an audio file (WAV, MP3, M4A, WebM, OGG)
3. Optionally add debate topic context
4. Click "🚀 Analyze My Argument"

### Results
- **📝 Transcription**: See what the AI heard
- **🎯 Score**: Get a rating from 1-10
- **😎 Emojis**: Visual reaction from AI Mina
- **💬 Comment**: Sassy, TikTok-style feedback
- **🎬 Avatar Video**: Watch AI avatar react (if HeyGen is configured)

## 🔧 Configuration Options

### Audio Recording Settings
- **Format**: WebM with Opus codec
- **Sample Rate**: 44.1kHz
- **Features**: Echo cancellation, noise suppression

### GPT-4 Scoring Criteria
- **1-3**: Terrible argument, no logic
- **4-5**: Weak argument, major flaws
- **6-7**: Decent argument, could be stronger
- **8-9**: Strong, well-reasoned argument
- **10**: Perfect argument, unbeatable logic

### Avatar Video Options
- **Resolution**: 1280x720 (16:9 aspect ratio)
- **Background**: Customizable (default: white)
- **Voice**: English (customizable)
- **Generation Time**: 1-3 minutes

## 🎯 Sample GPT Prompt

The AI judge uses this prompt structure:

```
You are a TikTok-style AI debate judge named "Mina" with a sassy, fun personality. 
The user just gave an argument and you need to react like you're in a viral TikTok video.

Your job:
1. Give a score from 1 to 10 (decimals allowed, e.g., 7.3)
2. Return 3-5 emojis that reflect your reaction
3. Provide a short, emotional comment (max 20 words)
4. Your tone should be expressive, fun, and viral-ready

Example output:
{
  "score": 7.3,
  "emojis": "😏🤔💥",
  "comment": "Not bad... but you lost me halfway. Pick a side!",
  "reasoning": "Good opening but argument became unclear"
}
```

## 🧪 Testing

### Test Individual Modules

```bash
# Test transcription
python whisper_transcribe.py

# Test GPT feedback
python gpt_feedback.py

# Test avatar generation
python avatar_gen.py

# Test complete pipeline
python scoring.py
```

### Test with Sample Audio
Place a test audio file named `test_audio.wav` in the project directory and run the test functions.

## 🚨 Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Make sure `.env` file exists and contains `OPENAI_API_KEY`
   - Restart the Streamlit app after adding the key

2. **"Could not access microphone"**
   - Allow microphone access in your browser
   - Use HTTPS in production (required for microphone access)

3. **"Transcription too short or invalid"**
   - Speak for at least 5-10 seconds
   - Ensure clear audio quality
   - Check microphone levels

4. **Avatar videos not working**
   - HeyGen API key is optional
   - Check your HeyGen account credits
   - Verify avatar ID is correct

### Browser Compatibility
- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Partial support (may need HTTPS for recording)
- **Edge**: Full support

## 🔒 Security & Privacy

- Audio files are processed temporarily and not permanently stored
- API keys are kept in environment variables
- No user data is logged or tracked
- All processing happens server-side

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
1. Set up HTTPS (required for microphone access)
2. Configure environment variables on your hosting platform
3. Ensure sufficient memory for audio processing
4. Consider rate limiting for API calls

### Recommended Platforms
- **Streamlit Cloud**: Easy deployment with GitHub integration
- **Heroku**: Full control with buildpacks
- **AWS/GCP**: Scalable cloud deployment
- **Railway**: Simple deployment with automatic HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Check the troubleshooting section
- **API Docs**: 
  - [OpenAI API](https://platform.openai.com/docs)
  - [HeyGen API](https://docs.heygen.com/)

## 🎉 What's Next?

Potential enhancements:
- Multiple AI judges with different personalities
- Argument categories and specialized scoring
- Social sharing integration
- Leaderboards and competitions
- Real-time debate battles
- Custom avatar creation
- Voice cloning for personalized reactions

---

**Built with ❤️ for the TikTok generation - where every argument deserves a viral reaction!** 🎤✨