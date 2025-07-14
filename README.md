# 🌿 Ayurveda Dosha Assessment

A comprehensive Ayurvedic dosha assessment tool that helps users discover their unique body constitution and receive personalized lifestyle and dietary recommendations.

## Features

- **20 Comprehensive Questions**: Based on traditional Ayurvedic principles
- **Dosha Calculation**: Automatic calculation of Vata, Pitta, and Kapha percentages
- **Personalized Advice**: Detailed dietary and lifestyle recommendations
- **Beautiful UI**: Modern, responsive design with smooth animations
- **Multiple Formats**: Available as both a web frontend and Streamlit app

## Files

- `questions.txt` - Contains all 20 assessment questions with dosha associations
- `streamlit_app.py` - Streamlit version for easy hosting
- `index.html`, `styles.css`, `script.js` - Web frontend version
- `ayurveda_agent.py` - Python backend with AI integration
- `requirements.txt` - Python dependencies

## Quick Start

### Option 1: Streamlit App (Recommended for hosting)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```

3. Open your browser to the provided URL (usually http://localhost:8501)

### Option 2: Web Frontend

1. Run the local server:
```bash
python server.py
```

2. Open your browser to http://localhost:8000

## Deploying to Streamlit Cloud

To share with your mom or others, deploy to Streamlit Cloud:

1. **Create a GitHub repository** and push your code:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/ayurveda-assessment.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set the path to your app: `streamlit_app.py`
   - Click "Deploy"

3. **Share the link** with your mom! The app will be available at a public URL like:
   `https://your-app-name-yourusername.streamlit.app`

## Local Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py

# Or run web frontend
python server.py
```

### File Structure

```
aiyurveda/
├── streamlit_app.py      # Main Streamlit app
├── questions.txt         # Assessment questions
├── index.html           # Web frontend
├── styles.css           # Web styling
├── script.js            # Web JavaScript
├── ayurveda_agent.py    # Python backend
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Customization

### Adding New Questions

Edit `questions.txt` following this format:
```
<Question 21>Your new question here?</Question 21>
<Option 1>Option text (Vata)</Option 1>
<Option 2>Option text (Pitta)</Option 2>
<Option 3>Option text (Kapha)</Option 3>
```

### Modifying Advice

Edit the `get_advice()` function in `streamlit_app.py` to customize the recommendations.

## Features

- ✅ **Interactive Assessment**: 20 questions with multiple choice answers
- ✅ **Dosha Calculation**: Automatic scoring of Vata, Pitta, and Kapha
- ✅ **Progress Tracking**: Visual progress bar and question counter
- ✅ **Beautiful Results**: Color-coded progress bars and detailed breakdown
- ✅ **Personalized Advice**: Comprehensive dietary and lifestyle recommendations
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **Easy Deployment**: One-click deployment to Streamlit Cloud

## Ayurvedic Principles

The assessment is based on traditional Ayurvedic dosha theory:

- **Vata (Air + Ether)**: Creative, quick-thinking, adaptable
- **Pitta (Fire + Water)**: Intelligent, focused, driven  
- **Kapha (Earth + Water)**: Strong, loyal, patient

Each dosha has specific dietary and lifestyle recommendations for optimal health and balance.

## License

This project is open source and available under the MIT License. 