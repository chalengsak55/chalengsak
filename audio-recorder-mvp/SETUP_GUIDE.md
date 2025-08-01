# 🚀 Quick Setup Guide - Argue with AI Avatar

Follow these steps to get your TikTok-style debate game running in minutes!

## ⚡ Quick Start (3 Steps)

### Step 1: Get Your API Keys
1. **OpenAI API Key** (Required):
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy it (you'll need it in Step 3)

2. **HeyGen API Key** (Optional for avatar videos):
   - Sign up at [HeyGen](https://www.heygen.com/)
   - Get your API key from dashboard
   - Choose an avatar ID from available avatars

### Step 2: Clone & Install
```bash
# Clone the project
git clone <your-repo-url>
cd audio-recorder-mvp

# Install Python dependencies
pip install -r requirements.txt
```

**If you get "externally-managed-environment" error:**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**If you get "python3-venv not available" error:**
```bash
# On Ubuntu/Debian
sudo apt install python3-venv
# Then retry the virtual environment creation
```

### Step 3: Configure API Keys
```bash
# Copy the template
cp .env.example .env

# Edit the .env file with your keys
nano .env  # or use any text editor
```

Add your keys to `.env`:
```env
OPENAI_API_KEY=sk-your-openai-key-here
HEYGEN_API_KEY=your-heygen-key-here  # Optional
HEYGEN_AVATAR_ID=your-avatar-id      # Optional
```

### Step 4: Run the App
```bash
streamlit run app.py
```

🎉 **That's it!** Open your browser to `http://localhost:8501`

## 🧪 Test Your Setup

### Quick Test
1. Open the app in your browser
2. Go to "Upload File" tab
3. Upload any audio file (or record using the microphone)
4. Click "Analyze My Argument"
5. You should see transcription and AI feedback!

### Module Tests
```bash
# Test individual components
python whisper_transcribe.py
python gpt_feedback.py
python avatar_gen.py
python scoring.py
```

## 🔧 Common Setup Issues

### 1. "OpenAI API key not found"
- Make sure your `.env` file is in the project root
- Check that `OPENAI_API_KEY` is spelled correctly
- Restart the Streamlit app after adding the key

### 2. "Could not access microphone"
- Allow microphone access in your browser
- For production, use HTTPS (required for microphone access)

### 3. "Module not found" errors
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### 4. HeyGen avatar videos not working
- This is optional! The app works without HeyGen
- Check your HeyGen account has credits
- Verify your avatar ID is correct

## 🌐 Browser Compatibility

✅ **Fully Supported:**
- Chrome (recommended)
- Firefox
- Edge

⚠️ **Partial Support:**
- Safari (may need HTTPS for recording)

## 💡 Pro Tips

1. **Better Audio Quality:**
   - Use a quiet environment
   - Speak clearly and at normal pace
   - Keep recordings 10-60 seconds for best results

2. **Faster Processing:**
   - Shorter audio files process faster
   - Clear speech = better transcription = better scores

3. **Avatar Videos:**
   - Takes 1-3 minutes to generate
   - Check status using the "Check Video Status" button
   - Videos are HD quality (1280x720)

## 🚀 Deployment Options

### Option 1: Streamlit Cloud (Easiest)
1. Push your code to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add your API keys in the app settings
4. Deploy with one click!

### Option 2: Local Network
```bash
# Run on all network interfaces
streamlit run app.py --server.address 0.0.0.0
```

### Option 3: Production Server
- Use HTTPS (required for microphone access)
- Set up proper environment variables
- Consider using Docker for containerization

## 📱 Mobile Usage

The app is mobile-friendly! Users can:
- Record audio directly on mobile browsers
- Upload audio files from their phone
- View results in a TikTok-style interface
- Share results easily

## 🎯 Usage Examples

### Great Arguments to Try:
- "Pineapple belongs on pizza because..."
- "Social media is ruining our generation because..."
- "Remote work is better than office work because..."
- "AI will help humanity, not replace it, because..."

### What Makes a Good Score:
- Clear, logical structure
- Specific examples
- Confident delivery
- Addressing counterarguments
- Strong conclusion

## 🆘 Need Help?

1. **Check the main README.md** for detailed documentation
2. **Run the test functions** to isolate issues
3. **Check browser console** for JavaScript errors
4. **Verify API keys** are working with simple tests

## 🎉 You're Ready!

Once you see the beautiful TikTok-style interface and can record/upload audio, you're all set! 

**Start arguing and let AI Mina judge your debate skills!** 🎤✨

---

*Having issues? The app works best with clear audio, valid API keys, and a modern browser. Most problems are solved by checking these three things!*