import streamlit as st
import json
import re
from typing import Dict, List
import os
from openai import OpenAI
from config import setup_openai_api_key, get_api_key_status

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
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    .user-message {
        background: #667eea;
        color: white;
        margin-left: 2rem;
    }
    .ai-message {
        background: #f8f9fa;
        color: #2c3e50;
        margin-right: 2rem;
    }
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_openai_client():
    """Initialize OpenAI client with API key"""
    api_key = setup_openai_api_key()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

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

def get_user_assessment_summary(answers: List[int], questions: List[Dict], scores: Dict[str, float]) -> str:
    """Create a summary of the user's assessment for the AI"""
    summary = "User's Ayurvedic Assessment Results:\n\n"
    
    # Add dosha scores
    summary += f"Dosha Constitution:\n"
    summary += f"- Vata: {scores['vata']:.1f}%\n"
    summary += f"- Pitta: {scores['pitta']:.1f}%\n"
    summary += f"- Kapha: {scores['kapha']:.1f}%\n\n"
    
    # Determine primary and secondary doshas
    sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_dosha = sorted_doshas[0][0]
    secondary_dosha = sorted_doshas[1][0]
    
    summary += f"Primary Constitution: {primary_dosha.title()} ({scores[primary_dosha]:.1f}%)\n"
    summary += f"Secondary Constitution: {secondary_dosha.title()} ({scores[secondary_dosha]:.1f}%)\n\n"
    
    # Add specific answers
    summary += "Assessment Responses:\n"
    for i, (answer, question) in enumerate(zip(answers, questions)):
        if answer is not None and answer < len(question['options']):
            selected_option = question['options'][answer]
            summary += f"Q{i+1}: {question['question']}\n"
            summary += f"A: {selected_option['text']} ({selected_option['dosha'].title() if selected_option['dosha'] else 'Neutral'})\n\n"
    
    return summary

def chat_with_ai(client: OpenAI, user_message: str, assessment_summary: str) -> str:
    """Chat with the AI Ayurvedic expert"""
    
    system_prompt = f"""You are an expert Ayurvedic practitioner with deep knowledge of doshas, diet, lifestyle, and natural healing. 

The user has completed an Ayurvedic dosha assessment. Here are their results:

{assessment_summary}

Based on this assessment, provide personalized, practical Ayurvedic advice. Consider their specific dosha constitution when answering questions about:
- Diet and nutrition
- Lifestyle and daily routine
- Exercise recommendations
- Stress management
- Seasonal considerations
- Specific health concerns

Always provide practical, actionable advice that the user can implement in their daily life. Use modern language while respecting traditional Ayurvedic principles. Be encouraging and supportive in your responses."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I apologize, but I'm having trouble connecting to the AI service. Please try again later. Error: {str(e)}"

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

# --- Main App Logic ---
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
    if 'show_chat' not in st.session_state:
        st.session_state.show_chat = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'openai_client' not in st.session_state:
        st.session_state.openai_client = setup_openai_api_key() and OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        progress = st.session_state.current_question / len(questions)
        st.progress(progress)
        st.caption(f"Question {st.session_state.current_question} of {len(questions)}")
        current_q = questions[st.session_state.current_question - 1]
        st.subheader(current_q['question'])

        # Use st.radio for answer selection
        answer_key = f"answer_{st.session_state.current_question}"
        if len(st.session_state.answers) < st.session_state.current_question:
            st.session_state.answers.append(None)
        options = [opt['text'] for opt in current_q['options']]
        answer_idx = st.session_state.answers[st.session_state.current_question-1]
        if answer_idx is not None:
            selected = st.radio(
                "Select an option:",
                options,
                index=answer_idx,
                key=answer_key
            )
        else:
            selected = st.radio(
                "Select an option:",
                options,
                key=answer_key
            )
        # Update answer in session_state
        for idx, opt in enumerate(current_q['options']):
            if selected == opt['text']:
                st.session_state.answers[st.session_state.current_question-1] = idx
                break

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.session_state.current_question > 1:
                if st.button("← Previous", key=f"prev_{st.session_state.current_question}"):
                    st.session_state.current_question -= 1
                    st.rerun()
        with col3:
            if st.session_state.answers[st.session_state.current_question-1] is not None:
                if st.session_state.current_question < len(questions):
                    if st.button("Next →", key=f"next_{st.session_state.current_question}"):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("Finish Assessment", key="finish"):
                        st.session_state.assessment_complete = True
                        st.rerun()

    # Results
    elif not st.session_state.show_advice and not st.session_state.show_chat:
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
        dosha_colors = {
            'vata': '#6C63FF',  # Indigo
            'pitta': '#FF9800', # Orange
            'kapha': '#43A047'  # Green
        }
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
                <div style="
                    background: linear-gradient(135deg, {dosha_colors[dosha]}22 0%, #222831 100%);
                    border-radius: 18px;
                    box-shadow: 0 4px 24px rgba(0,0,0,0.10);
                    padding: 2rem 1.2rem 1.2rem 1.2rem;
                    margin-bottom: 1.5rem;
                    border: 2px solid {dosha_colors[dosha]};
                    min-height: 180px;
                ">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 1.2rem; font-weight: 600; color: {dosha_colors[dosha]};">{dosha_names[dosha]}</span>
                        <span style="font-size: 2.2rem; font-weight: 700; color: {dosha_colors[dosha]};">{score:.1f}%</span>
                    </div>
                    <div style="margin: 0.7rem 0 0.5rem 0; width: 100%; height: 14px; background: #222831; border-radius: 7px; overflow: hidden;">
                        <div style="height: 100%; width: {score}%; background: {dosha_colors[dosha]}; border-radius: 7px; transition: width 1s;"></div>
                    </div>
                    <div style="font-size: 1rem; color: #e0e0e0; margin-top: 0.5rem; font-style: italic;">{dosha_descriptions[dosha]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Primary constitution summary
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #232526 0%, #414345 100%);
            color: #fff;
            padding: 2rem 1.5rem 1.5rem 1.5rem;
            border-radius: 18px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.10);
            border: 2px solid #6C63FF;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
        ">
            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.7rem; color: #fff;">Your Primary Constitution</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #6C63FF; margin-bottom: 0.5rem;">{dosha_names[primary_dosha]}</div>
            <div style="font-size: 1.05rem; color: #e0e0e0;">You are primarily a <b>{primary_dosha.title()}</b> type with <b>{secondary_dosha.title()}</b> as your secondary influence.</div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        st.markdown("""
        <div style="display: flex; gap: 1.5rem; justify-content: center; margin-top: 2.5rem; margin-bottom: 1.5rem;">
            <style>
            .ayur-btn {
                background: linear-gradient(90deg, #6C63FF 0%, #FF9800 100%);
                color: #fff !important;
                border: none;
                border-radius: 30px;
                padding: 0.9rem 2.2rem;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                margin: 0 0.2rem;
                box-shadow: 0 2px 8px rgba(108,99,255,0.10);
                transition: background 0.2s, transform 0.2s;
            }
            .ayur-btn:hover {
                background: linear-gradient(90deg, #FF9800 0%, #6C63FF 100%);
                transform: translateY(-2px);
            }
            </style>
            <form action="" method="post">
                <button class="ayur-btn" type="submit" name="take_again">Take Assessment Again</button>
                <button class="ayur-btn" type="submit" name="get_advice">Get Personalized Advice</button>
                <button class="ayur-btn" type="submit" name="chat_expert">Chat with AI Expert</button>
            </form>
        </div>
        """, unsafe_allow_html=True)

        # Button logic (keep Streamlit's actual buttons for functionality)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Take Assessment Again"):
                st.session_state.current_question = 0
                st.session_state.answers = []
                st.session_state.assessment_complete = False
                st.session_state.show_advice = False
                st.session_state.show_chat = False
                st.session_state.chat_messages = []
                st.rerun()
        with col2:
            if st.button("Get Personalized Advice"):
                st.session_state.show_advice = True
                st.rerun()
        with col3:
            if st.button("Chat with AI Expert"):
                st.session_state.show_chat = True
                st.rerun()
    
    # Advice screen
    elif st.session_state.show_advice:
        st.markdown('<h1 class="main-header">Your Personalized Ayurvedic Advice</h1>', unsafe_allow_html=True)
        
        # Calculate scores again for advice
        scores = calculate_dosha_scores(st.session_state.answers, questions)
        sorted_doshas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary_dosha = sorted_doshas[0][0]
        secondary_dosha = sorted_doshas[1][0]
        
        # Generate and display advice
        advice = get_advice(primary_dosha, secondary_dosha, scores)
        st.markdown(advice)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← Back to Results"):
                st.session_state.show_advice = False
                st.rerun()
        
        with col3:
            if st.button("Chat with AI Expert"):
                st.session_state.show_chat = True
                st.rerun()
    
    # Chat screen
    elif st.session_state.show_chat:
        st.markdown('<h1 class="main-header">Chat with Ayurvedic AI Expert</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Ask me anything about your health, lifestyle, or Ayurvedic practices based on your dosha constitution!</p>', unsafe_allow_html=True)
        
        # Calculate scores for context
        scores = calculate_dosha_scores(st.session_state.answers, questions)
        assessment_summary = get_user_assessment_summary(st.session_state.answers, questions, scores)
        
        # Display chat messages
        if st.session_state.chat_messages:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.chat_messages:
                if message['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message ai-message"><strong>AI Expert:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Ask your question:", key="chat_input", placeholder="e.g., What foods should I eat for breakfast? How can I improve my sleep?")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("Send Message", key="send_chat"):
                if user_input:
                    # Add user message to chat
                    st.session_state.chat_messages.append({"role": "user", "content": user_input})
                    
                    if st.session_state.openai_client:
                        # Get AI response
                        ai_response = chat_with_ai(st.session_state.openai_client, user_input, assessment_summary)
                        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                    else:
                        # Show error message
                        st.session_state.chat_messages.append({
                            "role": "assistant", 
                            "content": "I'm sorry, but the AI chat feature is currently unavailable. Please set up your OpenAI API key to use this feature."
                        })
                    
                    st.rerun()
        
        with col1:
            if st.button("← Back to Results"):
                st.session_state.show_chat = False
                st.rerun()
        
        with col3:
            if st.button("Clear Chat"):
                st.session_state.chat_messages = []
                st.rerun()

if __name__ == "__main__":
    main() 