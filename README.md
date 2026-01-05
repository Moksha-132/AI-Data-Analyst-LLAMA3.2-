# AI Data Insight Generator (Offline Explainable Analytics)

A professional, offline-first AI application for data analysis and explainable insights. This tool allows users to upload CSV datasets, generate automated analytical reports, and interact with an AI to understand the "why" behind the data.

## 🚀 Key Features

- **Local Authentication**: Secure SQLite-based user login and signup with `bcrypt` password hashing.
- **CSV Data Upload**: Easily upload and process large CSV datasets with automatic session-based data recovery.
- **Automated Analytics Pipeline**: Automatically detects anomalies, trends, and key performance indicators (KPIs).
- **Real-Time AI Chat**: Integrated "Talk to Data" interface with **Instant Streaming** for a snappy, real-time feel.
- **Performance Optimized**: Fine-tuned Llama 3.2 integration with keep-alive persistence and optimized token limits.
- **Offline-First**: Runs completely on your local machine, ensuring data privacy and zero dependency on cloud APIs.
- **Interactive Dashboard**: Modern UI with dynamic charts, data visualizations, and automated insights.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Data Processing**: Pandas, NumPy, Scikit-learn, SciPy
- **Database**: SQLite (for user auth)
- **AI/LLM**: Ollama (Llama 3.2)
- **Frontend**: HTML5, Vanilla CSS, JavaScript (Modern Aesthetics)
- **Visualization**: Chart.js / Dynamic Dashboard

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

1. **Python 3.8+**
2. **Ollama**: [Download Ollama](https://ollama.com/download)
3. **Llama 3.2 Model**: Run the following command after installing Ollama:
   ```bash
   ollama pull llama3.2:1b
   ```

> [!TIP]
> **Performance Tuning**: This app is optimized for speed. It uses `Llama 3.2:1b` with specialized parameters like `num_predict`, `num_ctx`, and `keep_alive` to ensure the chatbot responds instantly after the first load.

## ⚙️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Moksha-132/AI-Data-Analyst-LLAMA3.2-.git
   cd "Data Analyst"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the app**:
   Open your browser and navigate to `http://127.0.0.1:5000`.

## 📂 Project Structure

- `app.py`: Main Flask application and routing.
- `analytics/`: Core analytics pipeline and visualization logic.
- `auth/`: Database connection and authentication helpers.
- `llm/`: Integration with Ollama for AI insights and chat.
- `templates/`: HTML templates for the web interface.
- `static/`: CSS, JavaScript, and asset files.
- `utils/`: Common utility functions and parsers.

## � Author

**Lakshmi Moksha Boya**

## �📝 License

This project is for educational and professional data analysis purposes.
