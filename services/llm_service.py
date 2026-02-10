import os
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_with_groq(text: str) -> str:
    """Summarize using Groq API (FREE)"""
    
    message = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Free model
        messages=[
            {
                "role": "system",
                "content": "You are a professional meeting analyst. Summarize meetings concisely with key points, decisions, and action items."
            },
            {
                "role": "user",
                "content": f"Summarize this meeting transcript:\n\n{text}"
            }
        ],
        temperature=0.5,
        max_tokens=1000,
    )
    
    return message.choices[0].message.content

def summarize_with_gemini(text: str) -> str:
    """Summarize using Google Gemini API (FREE)"""
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    response = model.generate_content(f"""
    You are a professional meeting analyst. Analyze this meeting transcript and provide:
    1. Executive Summary (2-3 sentences)
    2. Key Decisions (bullet points)
    3. Action Items (bullet points)
    4. Topics Discussed (bullet points)
    
    Transcript:
    {text}
    """)
    
    return response.text

def extract_action_items(text: str, use_groq: bool = True) -> str:
    """Extract action items from text"""
    
    prompt = f"""
    Extract action items from this text. Format as a numbered list with:
    - What needs to be done
    - Who is responsible
    - When is it due
    
    Text:
    {text}
    """
    
    if use_groq:
        return summarize_with_groq(prompt)
    else:
        return summarize_with_gemini(prompt)

def extract_key_decisions(text: str, use_groq: bool = True) -> str:
    """Extract key decisions"""
    
    prompt = f"""
    Extract the key business decisions made in this text. List each decision clearly.
    
    Text:
    {text}
    """
    
    if use_groq:
        return summarize_with_groq(prompt)
    else:
        return summarize_with_gemini(prompt)