import requests
import json
import os

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')
MODEL_NAME = os.getenv('OLLAMA_MODEL', 'llama3.2:1b')

def _extract_data_context(profile_summary: dict, lean: bool = False) -> str:
    """Extracts raw statistical data. lean=True removes extra sections for speed."""
    profile = profile_summary.get('profile', {})
    trends = profile_summary.get('trends', {})
    correlations = profile_summary.get('correlations', {})
    anomalies = profile_summary.get('anomalies', {})

    # Nuclear Speed: ONLY row/col counts. No column stats.
    data_context = f"Data: {profile.get('rows')} rows, {profile.get('columns')} cols.\n"
    return data_context

def _format_prompt(profile_summary: dict, mode: str) -> str:
    """Create a structured prompt for LLaMA based on profiling data and selected mode."""
    data_context = _extract_data_context(profile_summary)

    # Mode-Specific Instructions
    # Mode-Specific Instructions
    if mode == 'exam':
        role = "You are a strict Data Science Professor evaluating a student's dataset."
        goal = "Explain the 'Why' and 'How' behind the metrics. Define statistical terms used (e.g., Standard Deviation, Correlation). Provide a deep, educational analysis."
        structure = """
MUST use this structure:
## 1. Executive Summary
(Brief overview)

## 2. Statistical Deep Dive
(Explain the metrics calculated. Why are they important? Define terms.)

## 3. Explanations & Reasoning
(Why did trends/anomalies happen? Hypothesize based on data.)

## 4. Exam-Style Questions & Recommendations
(What should the student investigate next? Ask a Viva question.)
"""
    else: # business (default)
        role = "You are a Senior Data Analyst consultant for a Fortune 500 company."
        goal = "Provide a comprehensive report including an Executive Summary followed by multiple analytical sections. Focus on business value, risks, and actionable next steps."
    structure = """
MUST use this structure for every section. Each insight MUST have these specific headings.
DO NOT put everything into one paragraph. Use these exact labels.

## [Insight Title]
Observation: [Strictly describe the DATA FACT or trend found.]
Root Cause (Why): [The technical, logical, or process reason WHY this exists.]
Business Impact: [The financial or operational consequence.]
Recommendation: [Specific actionable step to take.]
Confidence: [High/Medium/Low]

EXAMPLE:
## Revenue Performance
Observation: Sales increased by 15% in Q3.
Root Cause (Why): Strong demand for the new product line.
Business Impact: Higher quarterly profits.
Recommendation: Scale up production for Q4.
Confidence: High
"""
    prompt = f"""{role}
{goal}

DATA CONTEXT:
{data_context}

INSTRUCTIONS:
Analyze the data above and provide a detailed report.
1. Start with an ## Executive Summary (approx 2-3 sentences).
2. Then provide at least 3 detailed insight sections using the structure below:
{structure}
3. End with a ## Final Conclusion section. 
   For this section ONLY, use the following structure:
   ## Final Conclusion
   Observation: [Provide a brief, high-level summary of the entire analysis.]
   Confidence: [High/Medium/Low]
   (DO NOT add Root Cause, Impact, or Recommendation to the Conclusion.)
"""
    return prompt

def get_llama_explanation(profile_summary: dict, mode: str = 'business') -> str:
    """Send the formatted prompt to the local LLaMA model via Ollama."""
    prompt = _format_prompt(profile_summary, mode)
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.3 if mode == 'business' else 0.5, # Lower temp for business consistency
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
        data = response.json()
        return data.get('response', '').strip()
    except Exception as e:
        return f"Error communicating with Ollama: {e}"
def get_llama_chat_response(question: str, profile_summary: dict = None) -> str:
    """Ask LLaMA a question about the specific dataset context."""
    q_lower = question.lower().strip()
    if q_lower in {'hi', 'hello', 'hey', 'hi!', 'hello!', 'hey!'}:
        return "Hello! How can I help with your data today?"

    if profile_summary:
        data_section = "Context: " + _extract_data_context(profile_summary, lean=True)
    else:
        data_section = "Context: No data."

    chat_prompt = f"""{data_section}\nQ: {question}\nA (Concise):"""

    payload = {
        "model": MODEL_NAME,
        "prompt": chat_prompt,
        "stream": False,
        "temperature": 0.1,
        "options": {
            "num_predict": 512,
            "num_ctx": 2048,
            "num_thread": 4,
            "keep_alive": "30m"
        } 
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120) 
        response.raise_for_status()
        data = response.json()
        return data.get('response', '').strip()
    except Exception as e:
        return f"Error (Timeout - Model Loading): {str(e)}"

def get_llama_chat_stream(question: str, profile_summary: dict = None):
    """Yields LLaMA's response chunks instantly for greetings or via API for data."""
    q_lower = question.lower().strip()
    greetings = {'hi', 'hello', 'hey', 'hi!', 'hello!', 'hey!'}
    
    if q_lower in greetings:
        yield "Hello! How can I help with your data today?"
        return

    if profile_summary:
        data_section = "Context: " + _extract_data_context(profile_summary, lean=True)
    else:
        data_section = "Context: No data."

    chat_prompt = f"""{data_section}
Q: {question}
A (Concise):"""

    payload = {
        "model": MODEL_NAME,
        "prompt": chat_prompt,
        "stream": True,
        "temperature": 0.1,
        "options": {
            "num_predict": 512,
            "num_ctx": 2048,
            "num_thread": 4,
            "keep_alive": "30m"
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'response' in chunk:
                    yield chunk['response']
                if chunk.get('done'):
                    break
    except Exception as e:
        yield f" Error: {str(e)}"
