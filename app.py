import os
import json
import threading
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import pandas as pd

# Local imports
from auth.db import get_connection
from analytics.pipeline import run_analytics_pipeline
from llm.ollama import get_llama_explanation

app = Flask(__name__)
app.secret_key = 'dev-secret-key-data-analyst-123'  # Stability for development

# Configuration
UPLOAD_FOLDER = os.path.join(app.instance_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024  # 512 MB limit

# ---------------------------------------------------------------------------
# Helper functions for authentication (SQLite + bcrypt)
# ---------------------------------------------------------------------------
from passlib.hash import bcrypt

def verify_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return bcrypt.verify(password, row[0])
    return False

def create_user(username: str, password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    password_hash = bcrypt.hash(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        success = True
    except Exception:
        success = False
    finally:
        conn.close()
    return success

# ---------------------------------------------------------------------------
# Helper functions for AI Insights
# ---------------------------------------------------------------------------
def _ensure_insights(user, data):
    """Generates AI insights if missing for the user's current session."""
    if not data or data.get('insight') is not None:
        return data

    try:
        from llm.ollama import get_llama_explanation
        from utils.insight_parser import parse_insight_markdown
        
        mode = data.get('mode', 'business')
        summary = data.get('summary')
        
        if summary:
            raw_insight = get_llama_explanation(summary, mode=mode)
            parsed_insight = parse_insight_markdown(raw_insight)
            data['insight'] = parsed_insight
            # Update cache
            ANALYSIS_CACHE[user] = data
    except Exception as e:
        print(f"Error generating insights for {user}: {e}")
        data['insight'] = {}
    
    return data

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
# In-Memory Cache for Analysis Results
# Format: { 'username': { 'df': df, 'summary': dict, 'insight': dict, 'chart': dict } }
ANALYSIS_CACHE = {}

@app.route('/')
def home():
    # Hero image location – using the generated image from .gemini (absolute path)
    # Hero image is now served from static/images/hero.png
    hero_path = url_for('static', filename='images/hero.png')
    # For now, we assume it exists since we just moved it
    hero_exists = True 
    return render_template('home.html', hero_exists=hero_exists, hero_path=hero_path)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_user(username, password):
            session['authenticated'] = True
            session['username'] = username
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        if not username or not password:
            flash('Username and password cannot be empty.', 'warning')
        elif password != password_confirm:
            flash('Passwords do not match.', 'warning')
        else:
            if create_user(username, password):
                flash('Account created. Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username already taken.', 'danger')
    return render_template('signup.html')

def get_cached_data():
    user = session.get('username')
    data = ANALYSIS_CACHE.get(user)
    
    # Recovery Logic: If cache is empty but user had a file, reload it
    if not data and session.get('latest_filename'):
        filename = session['latest_filename']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                # Reload dataframe and summary
                df = run_analytics_pipeline(file_path)
                data = {
                    'df': df,
                    'summary': df.attrs.get('profile_summary'),
                    'insight': None,
                    'chart_data': None, # Will be regenerated on dashboard hit
                    'preview_html': df.head(10).to_html(classes='table table-striped', index=False),
                    'mode': 'business',
                    'filename': filename
                }
                ANALYSIS_CACHE[user] = data
                # Trigger insights in background again
                threading.Thread(target=_ensure_insights, args=(user, data)).start()
            except Exception:
                pass
    
    return data if data else {}

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('authenticated'):
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    user = session.get('username')
    
    # Handle File Upload & Analysis
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Run analytics pipeline
            df = run_analytics_pipeline(file_path)
            profile_summary = df.attrs.get('profile_summary')
            
            # Retrieve mode
            mode = request.form.get('mode', 'business')

            # Generate Visualization Data (Fast)
            from analytics.visualization import prepare_chart_data
            chart_data = prepare_chart_data(df, profile_summary)
            
            # Update Cache (Trigger LLM now for PDF completeness)
            data = {
                'df': df,
                'summary': profile_summary,
                'insight': None, 
                'chart_data': chart_data,
                'preview_html': df.head(10).to_html(classes='table table-striped', index=False),
                'mode': mode,
                'filename': filename
            }
            session['latest_filename'] = filename # For cache recovery
            
            # Generate insights immediately in a background thread
            threading.Thread(target=_ensure_insights, args=(user, data)).start()
            ANALYSIS_CACHE[user] = data

            return redirect(url_for('dashboard')) # PRG pattern
            
        else:
            flash('Please upload a valid CSV file.', 'danger')

    # Retrieve from cache
    data = get_cached_data()
    
    return render_template(
        'dashboard.html',
        # Only pass what's needed for the dashboard (KPIs + Charts)
        chart_data=data.get('chart_data'),
        # Extended Context for PDF Report
        insight=data.get('insight'), 
        preview_html=data.get('preview_html'),
        filename=data.get('filename', 'dataset.csv'),
        # Pass has_data flag to show empty state msg
        has_data=bool(data)
    )

@app.route('/insights')
def insights():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    data = get_cached_data()
    if not data:
        flash('Please upload data first.', 'warning')
        return redirect(url_for('dashboard'))

    # Insights are generated in the background. 
    # Just retrieve from cache.
    
    # Remove flash message if insight is missing, as it might be still generating
    # or the user finds it weird.
    pass

    return render_template(
        'insights.html',
        insight=data.get('insight'),
        has_data=bool(data)
    )

@app.route('/data')
def data_view():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    data = get_cached_data()
    return render_template(
        'data.html',
        preview_html=data.get('preview_html'),
        has_data=bool(data)
    )

@app.route('/logout')
def logout():
    user = session.get('username')
    if user in ANALYSIS_CACHE:
        del ANALYSIS_CACHE[user]
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat_api():
    if not session.get('authenticated'):
        return {'error': 'Unauthorized'}, 401
    
    user = session.get('username')
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return {'error': 'No question provided'}, 400
        
    cached_data = get_cached_data()
    # If no data, summary is None, which the LLM handles gracefully
    summary = cached_data.get('summary') if cached_data else None
        
    # Generate Answer via Streaming
    from llm.ollama import get_llama_chat_stream
    from flask import Response, stream_with_context

    def generate():
        for chunk in get_llama_chat_stream(question, summary):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
