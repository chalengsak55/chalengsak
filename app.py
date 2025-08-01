import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import numpy as np
import random

# Character prompts dictionary
CHARACTER_PROMPTS = {
    "👩 CEO Boss": [
        "Why do you think you deserve a raise?",
        "Why should I let you take time off next week?",
        "Convince me to not cancel your project."
    ],
    "🧑 Partner in a Breakup": [
        "Why do you think we should stay together?",
        "Tell me why it wasn't your fault this time.",
        "Convince me to forgive you."
    ],
    "👮 Strict Officer": [
        "Why were you driving so fast?",
        "Tell me why I shouldn't give you a ticket.",
        "Convince me you're not breaking the rules."
    ],
    "🧠 Debate Genius": [
        "Why should school uniforms be banned?",
        "Tell me why phones are good for students.",
        "Convince me video games help learning."
    ],
    "👻 Ghost of Your Toxic Ex": [
        "Why did you ghost me after everything?",
        "Tell me I was the best thing in your life.",
        "Convince me you've changed."
    ],
    "🧛 Vampire Landlord": [
        "Why are you always late on rent?",
        "Convince me to lower the rent this month.",
        "Tell me why I shouldn't evict you tonight."
    ],
    "🎤 Roast Battle Judge": [
        "Why are you funnier than your opponent?",
        "Convince me your joke wasn't offensive.",
        "Tell me why you should win this battle."
    ],
    "💸 MLM Salesperson Trying to Recruit You": [
        "Why should I quit my job and join you?",
        "Tell me how this isn't a pyramid scheme.",
        "Convince me I'll make money with your plan."
    ],
    "🔮 Psychic Who Thinks You're Lying": [
        "Why is your aura hiding the truth?",
        "Convince me you are telling the real story.",
        "Tell me what happened — and don't lie again."
    ]
}

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
        list(CHARACTER_PROMPTS.keys())
    )
    
    # Display randomly selected question for the chosen character
    if character:
        if f"selected_question_{character}" not in st.session_state:
            st.session_state[f"selected_question_{character}"] = random.choice(CHARACTER_PROMPTS[character])
        
        selected_question = st.session_state[f"selected_question_{character}"]
        
        st.subheader("Your challenge:")
        st.info(f"**{character}**: {selected_question}")
        
        # Button to get a new question
        if st.button("🎲 Get a different question"):
            st.session_state[f"selected_question_{character}"] = random.choice(CHARACTER_PROMPTS[character])
            st.rerun()
    
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
        if character:
            st.info(f"Question: {selected_question}")
        st.info(f"Difficulty level: {difficulty}")
        if record_video:
            st.info("Video and audio recording enabled")
        else:
            st.info("Audio-only recording enabled")

if __name__ == "__main__":
    main()