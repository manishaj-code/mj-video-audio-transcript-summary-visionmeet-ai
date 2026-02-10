import os
from groq import Groq
from google import genai  # Corrected for the new SDK
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq (Llama 3.3 is the perfect choice for Groq in 2026)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Gemini (New SDK style)
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def summarize_with_groq(text: str) -> str:
    """Summarize using Groq API (FREE)"""
    try:
        message = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
    except Exception as e:
        return f"❌ Groq Error: {str(e)}"

def summarize_with_gemini(text: str) -> str:
    """Summarize using Google Gemini API (New SDK)"""
    prompt = f"""
    You are a professional meeting analyst. Analyze this meeting transcript and provide:
    1. Executive Summary (2-3 sentences)
    2. Key Decisions (bullet points)
    3. Action Items (bullet points)
    4. Topics Discussed (bullet points)
    
    Transcript:
    {text}
    """
    
    try:
        # The new SDK uses client.models.generate_content
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"

def extract_action_items(text: str, use_groq: bool = True) -> str:
    """Extract action items from text"""
    prompt = f"Extract action items from this text. Format as a numbered list with: What, Who, and When.\n\nText: {text}"
    return summarize_with_groq(prompt) if use_groq else summarize_with_gemini(prompt)

def extract_key_decisions(text: str, use_groq: bool = True) -> str:
    """Extract key decisions"""
    prompt = f"Extract the key business decisions made in this text. List each clearly.\n\nText: {text}"
    return summarize_with_groq(prompt) if use_groq else summarize_with_gemini(prompt)