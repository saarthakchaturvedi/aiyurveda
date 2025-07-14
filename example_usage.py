#!/usr/bin/env python3
"""
Example usage of the Ayurveda AI Agent
"""

from ayurveda_agent import AyurvedaAgent
import os

def example_with_sample_data():
    """Example using sample dosha assessment data"""
    
    # Initialize the agent
    agent = AyurvedaAgent()
    
    # Sample dosha assessment responses (you can replace with actual responses)
    sample_responses = {
        "vata": [True, True, True, False, True, True, True, True, True, True],  # 90% vata
        "pitta": [False, True, False, True, True, True, False, True, False, True],  # 60% pitta
        "kapha": [False, False, False, False, False, False, False, False, True, True]  # 20% kapha
    }
    
    # Calculate dosha scores
    dosha_scores = agent.assess_dosha_constitution(sample_responses)
    
    print("🌿 Sample Ayurvedic Assessment Results 🌿")
    print("="*50)
    for dosha, score in dosha_scores.items():
        print(f"{dosha.capitalize()}: {score:.1f}%")
    
    # Get personalized advice
    user_concerns = "I have trouble sleeping and feel anxious often"
    advice = agent.get_personalized_advice(dosha_scores, user_concerns)
    
    print("\n" + "="*50)
    print("🌱 PERSONALIZED AYURVEDIC ADVICE")
    print("="*50)
    print(advice)

def run_interactive_assessment():
    """Run the full interactive assessment"""
    agent = AyurvedaAgent()
    agent.create_interactive_assessment()

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run interactive assessment")
    print("2. See example with sample data")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        run_interactive_assessment()
    elif choice == "2":
        example_with_sample_data()
    else:
        print("Invalid choice. Running interactive assessment...")
        run_interactive_assessment() 