import os
from openai import OpenAI
from typing import Dict, List, Optional
import json

class AyurvedaAgent:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Ayurveda AI Agent"""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.dosha_questions = self._get_dosha_assessment_questions()
        self.constitution_guidelines = self._get_constitution_guidelines()
        
    def _get_dosha_assessment_questions(self) -> Dict[str, List[str]]:
        """Return comprehensive dosha assessment questions"""
        return {
            "vata": [
                "Do you tend to have dry skin and hair?",
                "Do you often feel anxious or worried?",
                "Do you have irregular eating and sleeping patterns?",
                "Do you prefer warm weather over cold?",
                "Do you tend to be creative and enthusiastic?",
                "Do you have a thin, lean body frame?",
                "Do you speak quickly and move fast?",
                "Do you have difficulty gaining weight?",
                "Do you experience constipation frequently?",
                "Do you have a tendency to overthink?"
            ],
            "pitta": [
                "Do you have a medium build with good muscle tone?",
                "Do you tend to be competitive and ambitious?",
                "Do you have a strong appetite and get irritable when hungry?",
                "Do you prefer cool weather over hot?",
                "Do you have a sharp memory and good concentration?",
                "Do you tend to be organized and precise?",
                "Do you have a tendency toward anger or irritability?",
                "Do you have a warm body temperature?",
                "Do you have a medium-sized frame?",
                "Do you prefer cold drinks and foods?"
            ],
            "kapha": [
                "Do you have a large, solid body frame?",
                "Do you tend to be calm and patient?",
                "Do you have thick, oily skin and hair?",
                "Do you gain weight easily?",
                "Do you have a slow, steady walk?",
                "Do you prefer warm, dry weather?",
                "Do you have a deep, stable voice?",
                "Do you sleep deeply and for long periods?",
                "Do you have a strong immune system?",
                "Do you tend to be loyal and supportive?"
            ]
        }
    
    def _get_constitution_guidelines(self) -> Dict[str, Dict]:
        """Return guidelines for each dosha constitution"""
        return {
            "vata": {
                "description": "Vata is composed of Air and Ether elements. Vata types are creative, quick-thinking, and adaptable but can be prone to anxiety and irregular habits.",
                "diet": {
                    "favorable": ["Warm, cooked foods", "Sweet, sour, and salty tastes", "Ghee and oils", "Dairy products", "Nuts and seeds", "Root vegetables"],
                    "avoid": ["Cold, raw foods", "Bitter and astringent tastes", "Dry, light foods", "Carbonated drinks", "Caffeine"]
                },
                "lifestyle": {
                    "daily_routine": "Regular sleep schedule (10 PM - 6 AM), warm oil massage, gentle exercise like yoga and walking",
                    "exercise": "Gentle, grounding exercises like walking, swimming, tai chi, and restorative yoga",
                    "stress_management": "Meditation, deep breathing, warm baths, calming music"
                }
            },
            "pitta": {
                "description": "Pitta is composed of Fire and Water elements. Pitta types are intelligent, focused, and driven but can be prone to anger and inflammation.",
                "diet": {
                    "favorable": ["Cooling foods", "Sweet, bitter, and astringent tastes", "Fresh vegetables", "Sweet fruits", "Dairy products", "Grains"],
                    "avoid": ["Hot, spicy foods", "Sour and salty tastes", "Fermented foods", "Alcohol", "Red meat", "Excessive oil"]
                },
                "lifestyle": {
                    "daily_routine": "Early to bed (10 PM), early to rise (6 AM), cooling practices, moderate exercise",
                    "exercise": "Moderate exercise like swimming, cycling, and cooling yoga practices",
                    "stress_management": "Cooling meditation, moon gazing, spending time in nature"
                }
            },
            "kapha": {
                "description": "Kapha is composed of Earth and Water elements. Kapha types are strong, loyal, and patient but can be prone to weight gain and lethargy.",
                "diet": {
                    "favorable": ["Light, dry foods", "Bitter, pungent, and astringent tastes", "Honey", "Legumes", "Light vegetables", "Spices"],
                    "avoid": ["Heavy, oily foods", "Sweet, sour, and salty tastes", "Dairy products", "Cold foods", "Excessive water"]
                },
                "lifestyle": {
                    "daily_routine": "Early rising (6 AM), vigorous exercise, dry massage, stimulating practices",
                    "exercise": "Vigorous exercise like running, dancing, power yoga, and strength training",
                    "stress_management": "Stimulating activities, energizing music, social engagement"
                }
            }
        }
    
    def assess_dosha_constitution(self, responses: Dict[str, List[bool]]) -> Dict[str, float]:
        """Assess dosha constitution based on user responses"""
        dosha_scores = {"vata": 0, "pitta": 0, "kapha": 0}
        
        for dosha, answers in responses.items():
            if dosha in dosha_scores:
                dosha_scores[dosha] = sum(answers) / len(answers) * 100
        
        return dosha_scores
    
    def get_personalized_advice(self, dosha_scores: Dict[str, float], user_concerns: str = "") -> str:
        """Generate personalized Ayurvedic advice based on dosha constitution"""
        
        # Determine primary and secondary doshas
        sorted_doshas = sorted(dosha_scores.items(), key=lambda x: x[1], reverse=True)
        primary_dosha = sorted_doshas[0][0]
        secondary_dosha = sorted_doshas[1][0] if len(sorted_doshas) > 1 else None
        
        # Create prompt for AI
        prompt = f"""
        You are an expert Ayurvedic practitioner. Based on the following dosha assessment:

        Vata: {dosha_scores['vata']:.1f}%
        Pitta: {dosha_scores['pitta']:.1f}%
        Kapha: {dosha_scores['kapha']:.1f}%

        Primary dosha: {primary_dosha.capitalize()}
        Secondary dosha: {secondary_dosha.capitalize() if secondary_dosha else 'None'}

        User concerns: {user_concerns if user_concerns else 'General wellness'}

        Please provide comprehensive Ayurvedic advice including:
        1. Constitution analysis and what it means
        2. Dietary recommendations (what to eat more of, what to avoid)
        3. Lifestyle recommendations (daily routine, exercise, sleep)
        4. Specific remedies for any mentioned concerns
        5. Seasonal considerations
        6. Practical tips for implementation

        Make the advice practical, specific, and easy to follow. Use Ayurvedic principles but explain them in modern terms.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Ayurvedic practitioner with deep knowledge of doshas, diet, lifestyle, and natural healing. Provide practical, personalized advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating advice: {str(e)}"
    
    def get_dosha_questions(self) -> Dict[str, List[str]]:
        """Return the dosha assessment questions"""
        return self.dosha_questions
    
    def create_interactive_assessment(self) -> str:
        """Create an interactive dosha assessment"""
        print("🌿 Welcome to the Ayurvedic Dosha Assessment! 🌿")
        print("Please answer the following questions with 'yes' or 'no'.\n")
        
        responses = {"vata": [], "pitta": [], "kapha": []}
        
        for dosha, questions in self.dosha_questions.items():
            print(f"\n=== {dosha.upper()} Assessment ===")
            for i, question in enumerate(questions, 1):
                while True:
                    answer = input(f"{i}. {question} (yes/no): ").lower().strip()
                    if answer in ['yes', 'no']:
                        responses[dosha].append(answer == 'yes')
                        break
                    else:
                        print("Please answer 'yes' or 'no'.")
        
        # Calculate dosha scores
        dosha_scores = self.assess_dosha_constitution(responses)
        
        print("\n" + "="*50)
        print("📊 YOUR DOSHA RESULTS")
        print("="*50)
        for dosha, score in dosha_scores.items():
            print(f"{dosha.capitalize()}: {score:.1f}%")
        
        # Get user concerns
        print("\nWhat specific health concerns or goals would you like advice on?")
        concerns = input("(Press Enter if none): ").strip()
        
        # Generate personalized advice
        print("\n" + "="*50)
        print("🌱 YOUR PERSONALIZED AYURVEDIC ADVICE")
        print("="*50)
        
        advice = self.get_personalized_advice(dosha_scores, concerns)
        print(advice)
        
        return advice

def main():
    """Main function to run the Ayurveda Agent"""
    # Initialize the agent
    agent = AyurvedaAgent()
    
    # Run interactive assessment
    agent.create_interactive_assessment()

if __name__ == "__main__":
    main() 