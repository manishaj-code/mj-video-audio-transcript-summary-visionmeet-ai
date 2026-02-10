import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
import tempfile

# Import custom services
from services.transcription import transcribe_audio
from services.llm_service import summarize_with_groq, summarize_with_gemini
from services.speaker_detection import detect_speakers
from services.vector_search import embed_and_search, initialize_chroma
from services.video_processor import extract_audio_from_video

load_dotenv()

# Page config
st.set_page_config(
    page_title="VisionMeet AI",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar config
st.sidebar.title("⚙️ Settings")
llm_choice = st.sidebar.radio("Choose LLM:", ["Groq (Fast & Free)", "Gemini (Google)"])
st.sidebar.markdown("---")
st.sidebar.info("📚 Upload a video or audio file to get started!")

# Main title
st.title("🎥 VisionMeet AI")
st.markdown("### Extract insights from meetings in seconds")
st.markdown("---")

# Initialize session state
if "meeting_data" not in st.session_state:
    st.session_state.meeting_data = None
if "chroma_db" not in st.session_state:
    st.session_state.chroma_db = initialize_chroma()

# Tab 1: Upload & Process
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "📋 Summary", "🔍 Search", "👥 Speakers"])

with tab1:
    st.header("Upload Video or Audio")
    
    uploaded_file = st.file_uploader(
        "Choose a video or audio file",
        type=["mp4", "mov", "avi", "mp3", "wav", "m4a", "webm"]
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.audio(uploaded_file)
        
        with col2:
            st.info(f"📁 File: {uploaded_file.name}")
            st.info(f"📊 Size: {uploaded_file.size / (1024*1024):.2f} MB")
        
        if st.button("▶️ Process Video", type="primary", use_container_width=True):
            with st.spinner("⏳ Processing... This may take a few minutes"):

                # 1. INITIALIZE VARIABLE HERE
                audio_path = None
                
                # Save temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    tmp_path = tmp.name
                
                try:
                    progress_bar = st.progress(0)
                    status = st.status("Processing steps...", expanded=True)
                    
                    # Step 1: Extract audio
                    with status:
                        st.write("📢 Extracting audio...")
                    progress_bar.progress(20)
                    audio_path = extract_audio_from_video(tmp_path)
                    
                    # Step 2: Transcribe
                    with status:
                        st.write("✍️ Transcribing audio (Whisper)...")
                    progress_bar.progress(40)
                    transcript = transcribe_audio(audio_path)
                    
                    # Step 3: Detect speakers
                    with status:
                        st.write("👥 Detecting speakers...")
                    progress_bar.progress(60)
                    speakers_info = detect_speakers(audio_path, transcript)
                    
                    # Step 4: Summarize
                    with status:
                        st.write(f"💡 Summarizing with {llm_choice}...")
                    progress_bar.progress(80)
                    
                    if "Groq" in llm_choice:
                        summary = summarize_with_groq(transcript)
                    else:
                        summary = summarize_with_gemini(transcript)
                    
                    # Step 5: Create embeddings
                    with status:
                        st.write("🔗 Creating search embeddings...")
                    progress_bar.progress(95)
                    embed_and_search(transcript, uploaded_file.name, st.session_state.chroma_db)
                    
                    # Store meeting data
                    st.session_state.meeting_data = {
                        "filename": uploaded_file.name,
                        "transcript": transcript,
                        "summary": summary,
                        "speakers": speakers_info
                    }
                    
                    progress_bar.progress(100)
                    with status:
                        st.write("✅ Done!")
                    
                    st.success("✅ Video processed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    # Cleanup
                    os.remove(tmp_path)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)

# Tab 2: Summary
with tab2:
    st.header("📋 Meeting Summary")
    
    if st.session_state.meeting_data:
        meeting = st.session_state.meeting_data
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Summary")
            st.markdown(meeting["summary"])
        
        with col2:
            st.markdown("### Metadata")
            st.info(f"**File:** {meeting['filename']}\n\n**LLM Used:** {llm_choice}")
        
        # Extract action items
        st.markdown("### 📝 Action Items")
        action_prompt = f"Extract action items from this summary:\n{meeting['summary']}"
        
        if "Groq" in llm_choice:
            actions = summarize_with_groq(action_prompt)
        else:
            actions = summarize_with_gemini(action_prompt)
        
        st.markdown(actions)
        
        # Export transcript
        st.markdown("### 📄 Full Transcript")
        with st.expander("View Full Transcript"):
            transcript_text = "\n".join([chunk.get("text", "") for chunk in meeting["transcript"]])
            st.text_area("Transcript:", value=transcript_text, height=300, disabled=True)
            
            # Download button
            st.download_button(
                label="📥 Download Transcript",
                data=transcript_text,
                file_name=f"{meeting['filename']}_transcript.txt",
                mime="text/plain"
            )
    else:
        st.warning("⚠️ Upload a video first to see the summary")

# Tab 3: Search
with tab3:
    st.header("🔍 Search in Meeting")
    
    if st.session_state.meeting_data:
        query = st.text_input("Ask a question about the meeting:")
        
        if query and st.button("Search", type="primary", use_container_width=True):
            with st.spinner("🔍 Searching..."):
                results = embed_and_search(
                    query,
                    st.session_state.meeting_data["filename"],
                    st.session_state.chroma_db,
                    search_mode=True
                )
                
                if results:
                    st.success(f"Found {len(results)} relevant segments")
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Result {i}"):
                            st.markdown(result)
                else:
                    st.info("No relevant segments found")
    else:
        st.warning("⚠️ Upload a video first to search")

# Tab 4: Speaker Info
with tab4:
    st.header("👥 Speaker Information")
    
    if st.session_state.meeting_data and st.session_state.meeting_data.get("speakers"):
        speakers = st.session_state.meeting_data["speakers"]
        
        for speaker in speakers:
            with st.expander(f"👤 {speaker['name']} - {speaker['duration']}s"):
                st.markdown(f"**Total Speaking Time:** {speaker['duration']}s")
                st.markdown(f"**Segments:** {speaker['segments']}")
                st.markdown(f"**Sample:**\n{speaker['sample_text']}")
    else:
        st.warning("⚠️ Upload a video first to see speaker information")

# Footer
st.markdown("---")
st.markdown("""
### ℹ️ About VisionMeet AI
- 🎬 Transcribe videos using **Whisper**
- 🤖 Summarize using **Groq** or **Gemini** (free APIs)
- 👥 Detect speakers automatically
- 🔍 Search conversations by question
- 💾 Export transcripts and summaries

**Stack:** Streamlit | Groq | Gemini | Whisper | Python
""")