import streamlit as st
import json
import re
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="Ayurveda Dosha Assessment",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .dosha-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .progress-bar {
        background: #ecf0f1;
        height: 20px;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    .vata-fill { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
    .pitta-fill { background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); }
    .kapha-fill { background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); }
    .advice-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def load_questions() -> List[Dict]:
    """Load and parse questions from the questions.txt file"""
    try:
        with open('questions.txt', 'r', encoding='utf-8') as file:
            text = file.read()
        
        questions = []
        lines = text.split('\n')
        current_question = None
        current_options = []
        
        for line in lines:
            trimmed_line = line.strip()
            if not trimmed_line:
                continue
            
            # Check for question
            question_match = re.match(r'<Question (\d+)>(.*?)</Question \1>', trimmed_line)
            if question_match:
                # Save previous question if exists
                if current_question:
                    questions.append({
                        'question': current_question,
                        'options': current_options
                    })
                
                current_question = question_match.group(2)
                current_options = []
                continue
            
            # Check for option
            option_match = re.match(r'<Option (\d+)>(.*?)</Option \1>', trimmed_line)
            if option_match:
                option_text = option_match.group(2)
                dosha_match = re.search(r'\((Vata|Pitta|Kapha)\)$', option_text)
                dosha = dosha_match.group(1).lower() if dosha_match else None
                
                current_options.append({
                    'text': re.sub(r'\([^)]+\)$', '', option_text).strip(),
                    'dosha': dosha
                })
        
        # Add the last question
        if current_question:
            questions.append({
                'question': current_question,
                'options': current_options
            })
        
        return questions
    except FileNotFoundError:
        st.error("Questions file not found. Please make sure 'questions.txt' is in the same directory.")
        return []

def calculate_dosha_scores(answers: List[int], questions: List[Dict]) -> Dict[str, float]:
    """Calculate dosha scores based on user answers"""
    dosha_scores = {'vata': 0, 'pitta': 0, 'kapha': 0}
    
    for answer_index, question_index in enumerate(answers):
        if answer_index < len(questions) and question_index < len(questions[answer_index]['options']):
            selected_option = questions[answer_index]['options'][question_index]
            if selected_option['dosha']:
                dosha_scores[selected_option['dosha']] += 1
    
    # Convert to percentages
    total_answers = len([a for a in answers if a is not None])
    if total_answers > 0:
        for dosha in dosha_scores:
            dosha_scores[dosha] = (dosha_scores[dosha] / total_answers) * 100
    
    return dosha_scores

def get_advice(primary_dosha: str, secondary_dosha: str, scores: Dict[str, float]) -> str:
    """Generate personalized Ayurvedic advice"""
    
    advice_data = {
        'vata': {
            'description': 'Creative, quick-thinking, and adaptable. You tend to be energetic and imaginative but may experience anxiety and irregular habits.',
            'diet': {
                'favorable': ['Warm, cooked foods', 'Sweet, sour, and salty tastes', 'Ghee and oils', 'Dairy products', 'Nuts and seeds', 'Root vegetables'],
                'avoid': ['Cold, raw foods', 'Bitter and astringent tastes', 'Dry, light foods', 'Carbonated drinks', 'Caffeine']
            },
            'lifestyle': {
                'routine': 'Regular sleep schedule (10 PM - 6 AM), warm oil massage, gentle exercise like yoga and walking',
                'exercise': 'Gentle, grounding exercises like walking, swimming, tai chi, and restorative yoga',
                'stress': 'Meditation, deep breathing, warm baths, calming music'
            }
        },
        'pitta': {
            'description': 'Intelligent, focused, and driven. You are goal-oriented and competitive but may be prone to anger and inflammation.',
            'diet': {
                'favorable': ['Cooling foods', 'Sweet, bitter, and astringent tastes', 'Fresh vegetables', 'Sweet fruits', 'Dairy products', 'Grains'],
                'avoid': ['Hot, spicy foods', 'Sour and salty tastes', 'Fermented foods', 'Alcohol', 'Red meat', 'Excessive oil']
            },
            'lifestyle': {
                'routine': 'Early to bed (10 PM), early to rise (6 AM), cooling practices, moderate exercise',
                'exercise': 'Moderate exercise like swimming, cycling, and cooling yoga practices',
                'stress': 'Cooling meditation, moon gazing, spending time in nature'
            }
        },
        'kapha': {
            'description': 'Strong, loyal, and patient. You are dependable and nurturing but may be prone to weight gain and lethargy.',
            'diet': {
                'favorable': ['Light, dry foods', 'Bitter, pungent, and astringent tastes', 'Honey', 'Legumes', 'Light vegetables', 'Spices'],
                'avoid': ['Heavy, oily foods', 'Sweet, sour, and salty tastes', 'Dairy products', 'Cold foods', 'Excessive water']
            },
            'lifestyle': {
                'routine': 'Early rising (6 AM), vigorous exercise, dry massage, stimulating practices',
                'exercise': 'Vigorous exercise like running, dancing, power yoga, and strength training',
                'stress': 'Stimulating activities, energizing music, social engagement'
            }
        }
    }
    
    primary_advice = advice_data[primary_dosha]
    
    return f"""
    ## Your Personalized Ayurvedic Guidance
    
    ### Constitution Analysis
    Your primary constitution is **{primary_dosha.title()}** ({scores[primary_dosha]:.1f}%), 
    with **{secondary_dosha.title()}** ({scores[secondary_dosha]:.1f}%) as your secondary influence.
    
    **{primary_advice['description']}**
    
    ### Dietary Recommendations
    
    **Favor These Foods:**
    {chr(10).join([f"• {food}" for food in primary_advice['diet']['favorable']])}
    
    **Avoid or Minimize:**
    {chr(10).join([f"• {food}" for food in primary_advice['diet']['avoid']])}
    
    ### Lifestyle Recommendations
    
    **Daily Routine:**
    {primary_advice['lifestyle']['routine']}
    
    **Exercise:**
    {primary_advice['lifestyle']['exercise']}
    
    **Stress Management:**
    {primary_advice['lifestyle']['stress']}
    
    ### Seasonal Considerations
    As a {primary_dosha} type, pay special attention to balancing your constitution during seasonal changes. 
    Consider adjusting your diet and lifestyle practices accordingly.
    
    ### Practical Tips
    • Start with small changes and gradually incorporate these recommendations
    • Listen to your body and adjust practices as needed
    • Consider consulting with an Ayurvedic practitioner for personalized guidance
    • Maintain consistency in your daily routine for best results
    """

def main():
    # Initialize session state
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'show_advice' not in st.session_state:
        st.session_state.show_advice = False
    
    # Load questions
    questions = load_questions()
    
    if not questions:
        st.error("Unable to load questions. Please check the questions.txt file.")
        return
    
    # Welcome screen
    if st.session_state.current_question == 0 and not st.session_state.assessment_complete:
        st.markdown('<h1 class="main-header">🌿 Ayurveda Dosha Assessment 🌿</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Discover your unique body constitution and receive personalized Ayurvedic guidance</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Begin Assessment", key="start"):
                st.session_state.current_question = 1
                st.rerun()
    
    # Assessment
    elif not st.session_state.assessment_complete:
        # Progress bar
        progress = st.session_state.current_question / len(questions)
        st.progress(progress)
        st.caption(f"Question {st.session_state.current_question} of {len(questions)}")
        
        # Question
        current_q = questions[st.session_state.current_question - 1]
        st.subheader(current_q['question'])
        
        # Options
        selected_option = None
        for i, option in enumerate(current_q['options']):
            if st.button(f"{option['text']}", key=f"q{st.session_state.current_question}_opt{i}"):
                selected_option = i
                break
        
        # Navigation
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.session_state.current_question > 1:
                if st.button("← Previous", key=f"prev_{st.session_state.current_question}"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col3:
            if selected_option is not None:
                # Store answer
                while len(st.session_state.answers) < st.session_state.current_question:
                    st.session_state.answers.append(None)
                st.session_state.answers[st.session_state.current_question - 1] = selected_option
                
                if st.session_state.current_question < len(questions):
                    if st.button("Next →", key=f"next_{st.session_state.current_question}"):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("Finish Assessment", key="finish"):
                        st.session_state.assessment_complete = True
                        st.rerun()
    
    # Results
    elif not st.session_state.show_advice:
        st.markdown('<h1 class="main-header">Your Dosha Constitution</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Based on your responses, here\'s your unique body constitution breakdown:</p>', unsafe_allow_html=True)
        
        # Calculate scores
        scores = calculate_dosha_scores(st.session_state.answers, questions)
        
        # Sort doshas by score
        sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_dosha = sorted_doshas[0][0]
        secondary_dosha = sorted_doshas[1][0]
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        dosha_names = {
            'vata': 'Vata (Air + Ether)',
            'pitta': 'Pitta (Fire + Water)',
            'kapha': 'Kapha (Earth + Water)'
        }
        
        dosha_descriptions = {
            'vata': 'Creative, quick-thinking, adaptable',
            'pitta': 'Intelligent, focused, driven',
            'kapha': 'Strong, loyal, patient'
        }
        
        for i, (dosha, score) in enumerate(sorted_doshas):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div class="dosha-card">
                    <h3>{dosha_names[dosha]}</h3>
                    <h4>{score:.1f}%</h4>
                    <div class="progress-bar">
                        <div class="progress-fill {dosha}-fill" style="width: {score}%"></div>
                    </div>
                    <p><em>{dosha_descriptions[dosha]}</em></p>
                </div>
                """, unsafe_allow_html=True)
        
        # Primary constitution summary
        st.markdown(f"""
        <div class="advice-section">
            <h3>Your Primary Constitution</h3>
            <h4>{dosha_names[primary_dosha]}</h4>
            <p>You are primarily a {primary_dosha.title()} type with {secondary_dosha.title()} as your secondary influence.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Take Assessment Again"):
                st.session_state.current_question = 0
                st.session_state.answers = []
                st.session_state.assessment_complete = False
                st.session_state.show_advice = False
                st.rerun()
        
        with col3:
            if st.button("Get Personalized Advice"):
                st.session_state.show_advice = True
                st.rerun()
    
    # Advice screen
    else:
        st.markdown('<h1 class="main-header">Your Personalized Ayurvedic Advice</h1>', unsafe_allow_html=True)
        
        # Calculate scores again for advice
        scores = calculate_dosha_scores(st.session_state.answers, questions)
        sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_dosha = sorted_doshas[0][0]
        secondary_dosha = sorted_doshas[1][0]
        
        # Generate and display advice
        advice = get_advice(primary_dosha, secondary_dosha, scores)
        st.markdown(advice)
        
        if st.button("← Back to Results"):
            st.session_state.show_advice = False
            st.rerun()

if __name__ == "__main__":
    main() 