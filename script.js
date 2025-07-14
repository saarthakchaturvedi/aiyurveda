class AyurvedaAssessment {
    constructor() {
        this.questions = [];
        this.currentQuestion = 0;
        this.answers = [];
        this.doshaScores = { vata: 0, pitta: 0, kapha: 0 };
        
        this.initializeEventListeners();
        this.loadQuestions();
    }

    async loadQuestions() {
        try {
            const response = await fetch('questions.txt');
            const text = await response.text();
            this.parseQuestions(text);
        } catch (error) {
            console.error('Error loading questions:', error);
            // Fallback to hardcoded questions if file loading fails
            this.loadFallbackQuestions();
        }
    }

    parseQuestions(text) {
        const lines = text.split('\n');
        let currentQuestion = null;
        let currentOptions = [];

        for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;

            // Check for question
            const questionMatch = trimmedLine.match(/<Question (\d+)>(.*?)<\/Question \1>/);
            if (questionMatch) {
                // Save previous question if exists
                if (currentQuestion) {
                    this.questions.push({
                        question: currentQuestion,
                        options: currentOptions
                    });
                }
                
                currentQuestion = questionMatch[2];
                currentOptions = [];
                continue;
            }

            // Check for option
            const optionMatch = trimmedLine.match(/<Option (\d+)>(.*?)<\/Option \1>/);
            if (optionMatch) {
                const optionText = optionMatch[2];
                const doshaMatch = optionText.match(/\((Vata|Pitta|Kapha)\)$/);
                const dosha = doshaMatch ? doshaMatch[1].toLowerCase() : null;
                
                currentOptions.push({
                    text: optionText.replace(/\([^)]+\)$/, '').trim(),
                    dosha: dosha
                });
            }
        }

        // Add the last question
        if (currentQuestion) {
            this.questions.push({
                question: currentQuestion,
                options: currentOptions
            });
        }

        console.log('Parsed questions:', this.questions);
    }

    loadFallbackQuestions() {
        // Fallback questions if file loading fails
        this.questions = [
            {
                question: "What best describes your body frame?",
                options: [
                    { text: "Thin, light", dosha: "vata" },
                    { text: "Medium, muscular", dosha: "pitta" },
                    { text: "Broad, heavy", dosha: "kapha" }
                ]
            },
            {
                question: "How would you describe your skin type?",
                options: [
                    { text: "Dry, rough", dosha: "vata" },
                    { text: "Warm, oily, reddish", dosha: "pitta" },
                    { text: "Soft, moist, pale", dosha: "kapha" }
                ]
            }
        ];
    }

    initializeEventListeners() {
        // Start button
        document.getElementById('start-btn').addEventListener('click', () => {
            this.showScreen('assessment-screen');
            this.displayQuestion();
        });

        // Navigation buttons
        document.getElementById('prev-btn').addEventListener('click', () => {
            this.previousQuestion();
        });

        document.getElementById('next-btn').addEventListener('click', () => {
            this.nextQuestion();
        });

        // Results buttons
        document.getElementById('restart-btn').addEventListener('click', () => {
            this.restartAssessment();
        });

        document.getElementById('get-advice-btn').addEventListener('click', () => {
            this.showAdvice();
        });

        // Back to results
        document.getElementById('back-to-results').addEventListener('click', () => {
            this.showScreen('results-screen');
        });
    }

    showScreen(screenId) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        // Show target screen
        document.getElementById(screenId).classList.add('active');
    }

    displayQuestion() {
        if (this.currentQuestion >= this.questions.length) {
            this.calculateResults();
            return;
        }

        const question = this.questions[this.currentQuestion];
        document.getElementById('question-text').textContent = question.question;

        // Update progress
        const progress = ((this.currentQuestion + 1) / this.questions.length) * 100;
        document.getElementById('progress-fill').style.width = progress + '%';
        document.getElementById('progress-text').textContent = `Question ${this.currentQuestion + 1} of ${this.questions.length}`;

        // Display options
        const optionsContainer = document.getElementById('options-container');
        optionsContainer.innerHTML = '';

        question.options.forEach((option, index) => {
            const optionElement = document.createElement('div');
            optionElement.className = 'option';
            optionElement.textContent = option.text;
            optionElement.dataset.dosha = option.dosha;
            optionElement.dataset.index = index;

            // Check if this option was previously selected
            if (this.answers[this.currentQuestion] === index) {
                optionElement.classList.add('selected');
            }

            optionElement.addEventListener('click', () => {
                this.selectOption(optionElement, index);
            });

            optionsContainer.appendChild(optionElement);
        });

        // Update navigation buttons
        document.getElementById('prev-btn').disabled = this.currentQuestion === 0;
        document.getElementById('next-btn').textContent = 
            this.currentQuestion === this.questions.length - 1 ? 'Finish' : 'Next';
    }

    selectOption(optionElement, index) {
        // Remove selection from all options
        document.querySelectorAll('.option').forEach(opt => {
            opt.classList.remove('selected');
        });

        // Select clicked option
        optionElement.classList.add('selected');
        this.answers[this.currentQuestion] = index;
    }

    previousQuestion() {
        if (this.currentQuestion > 0) {
            this.currentQuestion--;
            this.displayQuestion();
        }
    }

    nextQuestion() {
        if (this.answers[this.currentQuestion] === undefined) {
            alert('Please select an option before continuing.');
            return;
        }

        if (this.currentQuestion < this.questions.length - 1) {
            this.currentQuestion++;
            this.displayQuestion();
        } else {
            this.calculateResults();
        }
    }

    calculateResults() {
        // Reset scores
        this.doshaScores = { vata: 0, pitta: 0, kapha: 0 };

        // Calculate scores based on answers
        this.answers.forEach((answerIndex, questionIndex) => {
            if (answerIndex !== undefined) {
                const question = this.questions[questionIndex];
                const selectedOption = question.options[answerIndex];
                
                if (selectedOption.dosha) {
                    this.doshaScores[selectedOption.dosha]++;
                }
            }
        });

        // Convert to percentages
        const totalAnswers = this.answers.filter(answer => answer !== undefined).length;
        if (totalAnswers > 0) {
            Object.keys(this.doshaScores).forEach(dosha => {
                this.doshaScores[dosha] = (this.doshaScores[dosha] / totalAnswers) * 100;
            });
        }

        this.displayResults();
    }

    displayResults() {
        // Update dosha percentages
        document.getElementById('vata-percentage').textContent = `${this.doshaScores.vata.toFixed(1)}%`;
        document.getElementById('pitta-percentage').textContent = `${this.doshaScores.pitta.toFixed(1)}%`;
        document.getElementById('kapha-percentage').textContent = `${this.doshaScores.kapha.toFixed(1)}%`;

        // Update progress bars
        document.getElementById('vata-bar').style.width = `${this.doshaScores.vata}%`;
        document.getElementById('pitta-bar').style.width = `${this.doshaScores.pitta}%`;
        document.getElementById('kapha-bar').style.width = `${this.doshaScores.kapha}%`;

        // Determine primary constitution
        const sortedDoshas = Object.entries(this.doshaScores)
            .sort(([,a], [,b]) => b - a);

        const primaryDosha = sortedDoshas[0];
        const primaryConstitution = document.getElementById('primary-constitution');
        
        const doshaNames = {
            vata: 'Vata (Air + Ether)',
            pitta: 'Pitta (Fire + Water)',
            kapha: 'Kapha (Earth + Water)'
        };

        const doshaDescriptions = {
            vata: 'Creative, quick-thinking, and adaptable. You tend to be energetic and imaginative but may experience anxiety and irregular habits.',
            pitta: 'Intelligent, focused, and driven. You are goal-oriented and competitive but may be prone to anger and inflammation.',
            kapha: 'Strong, loyal, and patient. You are dependable and nurturing but may be prone to weight gain and lethargy.'
        };

        primaryConstitution.innerHTML = `
            <h4>${doshaNames[primaryDosha[0]]}</h4>
            <p>${doshaDescriptions[primaryDosha[0]]}</p>
        `;

        this.showScreen('results-screen');
    }

    async showAdvice() {
        const adviceContent = document.getElementById('advice-content');
        adviceContent.innerHTML = '<p>Generating personalized advice...</p>';

        this.showScreen('advice-screen');

        try {
            // Create advice based on dosha scores
            const advice = this.generateAdvice();
            adviceContent.innerHTML = advice;
        } catch (error) {
            adviceContent.innerHTML = '<p>Error generating advice. Please try again.</p>';
        }
    }

    generateAdvice() {
        const sortedDoshas = Object.entries(this.doshaScores)
            .sort(([,a], [,b]) => b - a);
        
        const primaryDosha = sortedDoshas[0][0];
        const secondaryDosha = sortedDoshas[1][0];

        const advice = {
            vata: {
                diet: {
                    favorable: ['Warm, cooked foods', 'Sweet, sour, and salty tastes', 'Ghee and oils', 'Dairy products', 'Nuts and seeds', 'Root vegetables'],
                    avoid: ['Cold, raw foods', 'Bitter and astringent tastes', 'Dry, light foods', 'Carbonated drinks', 'Caffeine']
                },
                lifestyle: {
                    routine: 'Regular sleep schedule (10 PM - 6 AM), warm oil massage, gentle exercise like yoga and walking',
                    exercise: 'Gentle, grounding exercises like walking, swimming, tai chi, and restorative yoga',
                    stress: 'Meditation, deep breathing, warm baths, calming music'
                }
            },
            pitta: {
                diet: {
                    favorable: ['Cooling foods', 'Sweet, bitter, and astringent tastes', 'Fresh vegetables', 'Sweet fruits', 'Dairy products', 'Grains'],
                    avoid: ['Hot, spicy foods', 'Sour and salty tastes', 'Fermented foods', 'Alcohol', 'Red meat', 'Excessive oil']
                },
                lifestyle: {
                    routine: 'Early to bed (10 PM), early to rise (6 AM), cooling practices, moderate exercise',
                    exercise: 'Moderate exercise like swimming, cycling, and cooling yoga practices',
                    stress: 'Cooling meditation, moon gazing, spending time in nature'
                }
            },
            kapha: {
                diet: {
                    favorable: ['Light, dry foods', 'Bitter, pungent, and astringent tastes', 'Honey', 'Legumes', 'Light vegetables', 'Spices'],
                    avoid: ['Heavy, oily foods', 'Sweet, sour, and salty tastes', 'Dairy products', 'Cold foods', 'Excessive water']
                },
                lifestyle: {
                    routine: 'Early rising (6 AM), vigorous exercise, dry massage, stimulating practices',
                    exercise: 'Vigorous exercise like running, dancing, power yoga, and strength training',
                    stress: 'Stimulating activities, energizing music, social engagement'
                }
            }
        };

        const primaryAdvice = advice[primaryDosha];
        const secondaryAdvice = advice[secondaryDosha];

        return `
            <h2>Your Personalized Ayurvedic Guidance</h2>
            
            <h3>Constitution Analysis</h3>
            <p>Your primary constitution is <strong>${primaryDosha.charAt(0).toUpperCase() + primaryDosha.slice(1)}</strong> (${this.doshaScores[primaryDosha].toFixed(1)}%), 
            with <strong>${secondaryDosha.charAt(0).toUpperCase() + secondaryDosha.slice(1)}</strong> (${this.doshaScores[secondaryDosha].toFixed(1)}%) as your secondary influence.</p>

            <h3>Dietary Recommendations</h3>
            <h4>Favor These Foods:</h4>
            <ul>
                ${primaryAdvice.diet.favorable.map(food => `<li>${food}</li>`).join('')}
            </ul>
            
            <h4>Avoid or Minimize:</h4>
            <ul>
                ${primaryAdvice.diet.avoid.map(food => `<li>${food}</li>`).join('')}
            </ul>

            <h3>Lifestyle Recommendations</h3>
            <h4>Daily Routine:</h4>
            <p>${primaryAdvice.lifestyle.routine}</p>
            
            <h4>Exercise:</h4>
            <p>${primaryAdvice.lifestyle.exercise}</p>
            
            <h4>Stress Management:</h4>
            <p>${primaryAdvice.lifestyle.stress}</p>

            <h3>Seasonal Considerations</h3>
            <p>As a ${primaryDosha} type, pay special attention to balancing your constitution during seasonal changes. 
            Consider adjusting your diet and lifestyle practices accordingly.</p>

            <h3>Practical Tips</h3>
            <ul>
                <li>Start with small changes and gradually incorporate these recommendations</li>
                <li>Listen to your body and adjust practices as needed</li>
                <li>Consider consulting with an Ayurvedic practitioner for personalized guidance</li>
                <li>Maintain consistency in your daily routine for best results</li>
            </ul>
        `;
    }

    restartAssessment() {
        this.currentQuestion = 0;
        this.answers = [];
        this.doshaScores = { vata: 0, pitta: 0, kapha: 0 };
        this.showScreen('welcome-screen');
    }
}

// Initialize the assessment when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new AyurvedaAssessment();
}); 