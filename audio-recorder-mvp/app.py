"""
Streamlit Main App - Argue with AI Avatar MVP
Complete TikTok-style debate game interface
"""

import streamlit as st
import os
import tempfile
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import base64

from scoring import ArgumentScorer

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🎤 Argue with AI Avatar",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for TikTok-style UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .score-display {
        text-align: center;
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .emoji-display {
        text-align: center;
        font-size: 3rem;
        margin: 1rem 0;
    }
    
    .comment-display {
        text-align: center;
        font-size: 1.5rem;
        font-style: italic;
        color: #666;
        margin: 1rem 0;
    }
    
    .result-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .transcription-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .status-success { background-color: #28a745; }
    .status-error { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; color: black; }
    .status-info { background-color: #17a2b8; }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'scorer' not in st.session_state:
        st.session_state.scorer = None
    if 'processing_results' not in st.session_state:
        st.session_state.processing_results = None
    if 'audio_uploaded' not in st.session_state:
        st.session_state.audio_uploaded = False
    if 'video_status_checked' not in st.session_state:
        st.session_state.video_status_checked = False

def initialize_scorer():
    """Initialize the argument scorer with API keys"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        heygen_key = os.getenv('HEYGEN_API_KEY')
        heygen_avatar = os.getenv('HEYGEN_AVATAR_ID')
        
        if not openai_key:
            st.error("❌ OpenAI API key not found! Please set OPENAI_API_KEY in your .env file.")
            return None
        
        # Enable avatar only if HeyGen keys are available
        enable_avatar = bool(heygen_key and heygen_avatar)
        
        scorer = ArgumentScorer(
            openai_api_key=openai_key,
            heygen_api_key=heygen_key,
            heygen_avatar_id=heygen_avatar,
            enable_avatar=enable_avatar
        )
        
        return scorer
        
    except Exception as e:
        st.error(f"❌ Failed to initialize scorer: {str(e)}")
        return None

def display_header():
    """Display the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎤 Argue with AI Avatar</h1>
        <p>Record your argument and let AI judge your debate skills!</p>
        <p><em>TikTok-style reactions • Real-time scoring • AI Avatar feedback</em></p>
    </div>
    """, unsafe_allow_html=True)

def display_audio_recorder():
    """Display the audio recording interface"""
    st.markdown("### 🎙️ Record Your Argument")
    
    # Embed the HTML audio recorder
    with open("audio-recorder.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Display the recorder in an iframe-like component
    st.components.v1.html(html_content, height=600, scrolling=False)
    
    st.markdown("---")

def handle_audio_upload():
    """Handle audio file upload"""
    st.markdown("### 📁 Or Upload Audio File")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'webm', 'ogg'],
        help="Upload your recorded argument (max 25MB)"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Add context input
        context = st.text_input(
            "Debate Topic (optional)",
            placeholder="e.g., 'Pineapple on pizza debate'",
            help="Provide context to help the AI understand your argument better"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Analyze My Argument", key="upload_analyze"):
                process_uploaded_audio(uploaded_file, context)

def process_uploaded_audio(uploaded_file, context=None):
    """Process uploaded audio file"""
    if st.session_state.scorer is None:
        st.error("❌ Scorer not initialized. Please check your API keys.")
        return
    
    try:
        # Show processing status
        status_placeholder = st.empty()
        progress_bar = st.progress(0)
        
        with status_placeholder.container():
            st.markdown('<div class="status-indicator status-info">🔄 Processing your argument...</div>', unsafe_allow_html=True)
        
        # Read audio file
        audio_data = uploaded_file.read()
        progress_bar.progress(20)
        
        # Process the audio
        with st.spinner("Transcribing audio..."):
            results = st.session_state.scorer.process_audio_blob(
                audio_data, 
                uploaded_file.name, 
                context
            )
            progress_bar.progress(100)
        
        # Store results
        st.session_state.processing_results = results
        st.session_state.audio_uploaded = True
        
        # Clear status
        status_placeholder.empty()
        progress_bar.empty()
        
        # Display results
        display_results(results)
        
    except Exception as e:
        st.error(f"❌ Processing failed: {str(e)}")

def display_results(results):
    """Display processing results with TikTok-style UI"""
    if not results:
        return
    
    st.markdown("## 🎯 Your Argument Results")
    
    # Success/Error status
    if results.get("success"):
        st.success("✅ Analysis complete!")
    else:
        st.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
        return
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Transcription
        transcription = results.get("transcription", {})
        if transcription.get("success"):
            st.markdown("### 📝 What You Said")
            st.markdown(f"""
            <div class="transcription-box">
                <strong>Transcription:</strong><br>
                "{transcription.get('text', 'No text available')}"
            </div>
            """, unsafe_allow_html=True)
            
            # Transcription metadata
            if transcription.get("language"):
                st.caption(f"Language: {transcription['language']} | Duration: {transcription.get('duration', 'Unknown')}s")
    
    with col2:
        # Feedback display
        feedback = results.get("feedback", {})
        if feedback.get("success"):
            st.markdown("### 🤖 AI Mina's Reaction")
            
            # Score
            score = feedback.get("score", 0)
            st.markdown(f'<div class="score-display">{score}/10</div>', unsafe_allow_html=True)
            
            # Emojis
            emojis = feedback.get("emojis", "🤔")
            st.markdown(f'<div class="emoji-display">{emojis}</div>', unsafe_allow_html=True)
            
            # Comment
            comment = feedback.get("comment", "No comment available")
            st.markdown(f'<div class="comment-display">"{comment}"</div>', unsafe_allow_html=True)
            
            # Reasoning (if available)
            if feedback.get("reasoning"):
                st.caption(f"💭 {feedback['reasoning']}")
    
    # Avatar video section
    avatar_result = results.get("avatar_video", {})
    if avatar_result and avatar_result.get("success"):
        st.markdown("### 🎬 AI Avatar Reaction")
        
        video_id = avatar_result.get("video_id")
        if video_id:
            st.info(f"🎥 Avatar video is being generated... Video ID: {video_id}")
            
            # Add button to check video status
            if st.button("🔄 Check Video Status", key="check_video"):
                check_avatar_video_status(video_id)
        else:
            st.warning("Avatar video generation started but no video ID received.")
    
    elif avatar_result and avatar_result.get("status") == "disabled":
        st.info("💡 Avatar videos are disabled. Add HeyGen API key to enable AI avatar reactions!")
    
    # Action buttons
    st.markdown("### 🎬 Share Your Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Try Again", key="try_again"):
            st.session_state.processing_results = None
            st.session_state.audio_uploaded = False
            st.rerun()
    
    with col2:
        if st.button("💾 Save Results", key="save_results"):
            save_results_to_file(results)
    
    with col3:
        if st.button("📊 View Details", key="view_details"):
            display_detailed_results(results)

def check_avatar_video_status(video_id):
    """Check the status of avatar video generation"""
    if st.session_state.scorer is None:
        st.error("❌ Scorer not initialized.")
        return
    
    try:
        with st.spinner("Checking video status..."):
            status_result = st.session_state.scorer.get_avatar_video_status(video_id)
        
        if status_result.get("success"):
            status = status_result.get("status")
            
            if status == "completed":
                video_url = status_result.get("video_url")
                if video_url:
                    st.success("✅ Avatar video is ready!")
                    st.video(video_url)
                else:
                    st.warning("Video completed but no URL available.")
            
            elif status in ["generating", "pending"]:
                st.info(f"🔄 Video is still generating... Status: {status}")
                st.info("💡 Tip: Video generation usually takes 1-3 minutes.")
            
            elif status == "failed":
                st.error("❌ Video generation failed.")
            
            else:
                st.warning(f"⚠️ Unknown status: {status}")
        
        else:
            st.error(f"❌ Failed to check status: {status_result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Status check failed: {str(e)}")

def save_results_to_file(results):
    """Save results to a downloadable JSON file"""
    try:
        # Create JSON string
        json_str = json.dumps(results, indent=2, ensure_ascii=False)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"argument_results_{timestamp}.json"
        
        # Create download button
        st.download_button(
            label="📥 Download Results",
            data=json_str,
            file_name=filename,
            mime="application/json",
            key="download_results"
        )
        
        st.success("✅ Results prepared for download!")
        
    except Exception as e:
        st.error(f"❌ Failed to prepare download: {str(e)}")

def display_detailed_results(results):
    """Display detailed results in an expandable section"""
    with st.expander("📊 Detailed Analysis Results", expanded=False):
        
        # Processing steps
        st.markdown("#### 🔄 Processing Steps")
        steps = results.get("processing_steps", [])
        for i, step in enumerate(steps, 1):
            st.text(f"{i}. {step}")
        
        # Full transcription data
        transcription = results.get("transcription", {})
        if transcription:
            st.markdown("#### 📝 Transcription Details")
            st.json(transcription)
        
        # Full feedback data
        feedback = results.get("feedback", {})
        if feedback:
            st.markdown("#### 🤖 Feedback Details")
            st.json(feedback)
        
        # Avatar video data
        avatar = results.get("avatar_video", {})
        if avatar:
            st.markdown("#### 🎬 Avatar Video Details")
            st.json(avatar)
        
        # Raw results
        st.markdown("#### 🔍 Raw Results")
        st.json(results)

def display_sidebar_info():
    """Display information in the sidebar"""
    with st.sidebar:
        st.markdown("## ℹ️ About")
        st.markdown("""
        **Argue with AI Avatar** is a TikTok-style debate game where you:
        
        1. 🎤 Record your argument
        2. 🤖 Get AI feedback from "Mina"
        3. 📹 Watch AI avatar reaction (optional)
        4. 📊 Share your results
        
        ### 🔧 Features
        - Real-time audio recording
        - AI transcription (Whisper)
        - Smart argument scoring (GPT-4)
        - Avatar video reactions (HeyGen)
        - Shareable results
        
        ### 🚀 Tech Stack
        - Streamlit (Frontend)
        - OpenAI APIs (Whisper + GPT-4)
        - HeyGen API (Avatar videos)
        - Python backend
        """)
        
        # API status
        st.markdown("### 🔑 API Status")
        
        openai_key = os.getenv('OPENAI_API_KEY')
        heygen_key = os.getenv('HEYGEN_API_KEY')
        
        if openai_key:
            st.success("✅ OpenAI API configured")
        else:
            st.error("❌ OpenAI API key missing")
        
        if heygen_key:
            st.success("✅ HeyGen API configured")
        else:
            st.warning("⚠️ HeyGen API key missing (Avatar videos disabled)")

def main():
    """Main application function"""
    # Initialize session state
    init_session_state()
    
    # Display header
    display_header()
    
    # Initialize scorer if needed
    if st.session_state.scorer is None:
        st.session_state.scorer = initialize_scorer()
    
    # Show sidebar info
    display_sidebar_info()
    
    # Main content
    if st.session_state.scorer is None:
        st.error("❌ Application not properly configured. Please check your API keys in the .env file.")
        st.markdown("""
        ### 🔧 Setup Instructions:
        1. Copy `.env.example` to `.env`
        2. Add your OpenAI API key
        3. Optionally add HeyGen API keys for avatar videos
        4. Restart the application
        """)
        return
    
    # Check if we have results to display
    if st.session_state.processing_results:
        display_results(st.session_state.processing_results)
        st.markdown("---")
    
    # Audio recording/upload interface
    tab1, tab2 = st.tabs(["🎤 Record Audio", "📁 Upload File"])
    
    with tab1:
        display_audio_recorder()
    
    with tab2:
        handle_audio_upload()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>🎤 <strong>Argue with AI Avatar</strong> - TikTok-style Debate Game MVP</p>
        <p><em>Built with Streamlit, OpenAI APIs, and HeyGen</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()