import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import numpy as np

# Audio processor class
class AudioProcessor:
    def __init__(self):
        pass
    
    def recv(self, frame):
        # Just pass audio through
        return frame

def main():
    st.title("🎙 Argue with AI")
    
    # Character selection
    st.subheader("Choose your AI opponent:")
    character = st.selectbox(
        "Select character:",
        [
            "👩 CEO Boss",
            "🧑 Partner in a breakup", 
            "👮 Strict Officer",
            "🧠 Debate Genius"
        ]
    )
    
    # Difficulty level
    st.subheader("Select difficulty level:")
    difficulty = st.radio(
        "Difficulty:",
        ["Beginner", "Intermediate", "Hard"]
    )
    
    # Video recording option
    record_video = st.checkbox("Also record my face (optional)")
    
    # WebRTC configuration
    rtc_configuration = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    })
    
    # WebRTC streamer
    st.subheader("Record your argument:")
    
    if record_video:
        # Video + Audio recording
        webrtc_ctx = webrtc_streamer(
            key="argue-with-ai-video",
            mode=WebRtcMode.SENDONLY,
            rtc_configuration=rtc_configuration,
            video_processor_factory=None,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={
                "video": True,
                "audio": True
            }
        )
    else:
        # Audio only recording
        webrtc_ctx = webrtc_streamer(
            key="argue-with-ai-audio", 
            mode=WebRtcMode.SENDONLY,
            rtc_configuration=rtc_configuration,
            video_processor_factory=None,
            audio_processor_factory=AudioProcessor,
            media_stream_constraints={
                "video": False,
                "audio": True
            }
        )
    
    # Submit button
    if st.button("Submit My Argument"):
        st.success("🚀 Processing your argument... (Feature coming soon!)")
        st.info(f"Selected character: {character}")
        st.info(f"Difficulty level: {difficulty}")
        if record_video:
            st.info("Video and audio recording enabled")
        else:
            st.info("Audio-only recording enabled")

if __name__ == "__main__":
    main()