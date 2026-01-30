"""
Psychology Assistant Agent using MentalBERT

This agent provides mental health support and counseling using MentalBERT,
a BERT model fine-tuned on mental health conversations and Reddit posts.
Uses Google Gemini for natural language response generation.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging
from typing import Dict, List, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PsychologyAssistant:
    """
    Psychology Assistant using MentalBERT for mental health support.
    
    MentalBERT is a domain-specific BERT model trained on mental health data
    from various sources including Reddit mental health communities.
    """
    
    def __init__(self, gemini_llm=None):
        """
        Initialize the Psychology Assistant with MentalBERT model and Gemini LLM.
        
        Args:
            gemini_llm: Optional Gemini LLM instance. If not provided, will create one.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load MentalBERT model and tokenizer
        self.model_name = "mental/mental-bert-base-uncased"
        
        try:
            logger.info("Loading MentalBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=7,  # Mental health categories
                problem_type="multi_label_classification"
            ).to(self.device)
            self.model.eval()
            logger.info("MentalBERT model loaded successfully!")
            
        except Exception as e:
            logger.warning(f"Could not load MentalBERT from HuggingFace: {e}")
            logger.info("Falling back to base BERT model...")
            # Fallback to base model
            self.model_name = "bert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=7
            ).to(self.device)
            self.model.eval()
        
        # Mental health categories
        self.categories = [
            "anxiety",
            "depression",
            "stress",
            "bipolar",
            "ptsd",
            "suicide_watch",
            "general_mental_health"
        ]
        
        # Initialize Google Gemini for response generation
        try:
            if gemini_llm is not None:
                self.gemini_llm = gemini_llm
                logger.info("Using provided Gemini LLM for response generation")
            else:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from dotenv import load_dotenv
                import os
                
                load_dotenv()
                logger.info("Initializing Google Gemini for response generation...")
                self.gemini_llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    temperature=0.7,
                    convert_system_message_to_human=True
                )
                logger.info("Google Gemini initialized successfully!")
        except Exception as e:
            logger.error(f"Could not initialize Gemini: {e}")
            self.gemini_llm = None
    
    def analyze_mental_state(self, text: str) -> Dict[str, float]:
        """
        Analyze the mental health state from user's text.
        
        Args:
            text: User's input text
            
        Returns:
            Dictionary with mental health category probabilities
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.sigmoid(logits).cpu().numpy()[0]
            
            # Create result dictionary
            results = {
                category: float(prob)
                for category, prob in zip(self.categories, probabilities)
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing mental state: {e}")
            return {cat: 0.0 for cat in self.categories}
    
    def generate_supportive_response(
        self,
        user_input: str,
        mental_state: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Generate a supportive, empathetic response using Google Gemini.
        
        Args:
            user_input: User's message
            mental_state: Detected mental health state probabilities
            
        Returns:
            Empathetic and supportive response
        """
        try:
            if mental_state is None:
                mental_state = self.analyze_mental_state(user_input)
            
            # Get the primary concern
            primary_concern = max(mental_state.items(), key=lambda x: x[1])
            concern_name, concern_score = primary_concern
            
            # Generate contextual response based on concern
            responses = self._get_response_templates(concern_name, concern_score)
            
            # If we have Gemini LLM, use it for more natural responses
            if self.gemini_llm and concern_score > 0.5:
                prompt = f"""You are a compassionate mental health counselor. Respond to this person who needs support:

User's message: "{user_input}"

Analysis shows the person may be experiencing: {concern_name} (confidence: {concern_score:.0%})

Provide a warm, empathetic response that includes:
1. Empathetic acknowledgment of their feelings
2. Supportive and validating language
3. 2-3 practical coping strategies they can try immediately
4. Gentle encouragement to seek professional help if needed
5. Crisis resources if the situation seems urgent

Keep your response concise (under 300 words), warm, and actionable. Avoid medical jargon. Be human and caring.

Response:"""
                
                try:
                    response = self.gemini_llm.invoke(prompt)
                    # Extract content from response
                    if hasattr(response, 'content'):
                        return response.content
                    return str(response)
                except Exception as e:
                    logger.warning(f"Gemini generation failed: {e}, using template")
            
            # Use template response as fallback
            return responses[0]
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_fallback_response()
    
    def _get_response_templates(
        self,
        concern: str,
        score: float
    ) -> List[str]:
        """Get appropriate response templates based on detected concern."""
        
        templates = {
            "anxiety": [
                "I understand you're experiencing anxiety. It's completely valid to feel this way. "
                "Here are some immediate techniques that might help:\n\n"
                "1. **Deep Breathing**: Try the 4-7-8 technique (breathe in for 4, hold for 7, exhale for 8)\n"
                "2. **Grounding Exercise**: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste\n"
                "3. **Progressive Muscle Relaxation**: Tense and release each muscle group\n\n"
                "Remember, anxiety is treatable. Consider reaching out to a mental health professional for personalized support.",
                
                "Anxiety can feel overwhelming, but you're not alone. Many people experience this. "
                "Try to focus on what you can control right now. Would you like to talk about specific situations "
                "that trigger your anxiety?"
            ],
            
            "depression": [
                "I hear you, and I want you to know that what you're feeling is real and valid. "
                "Depression is a medical condition, not a weakness. Here's what might help:\n\n"
                "1. **Small Steps**: Even tiny accomplishments matter - getting out of bed, taking a shower\n"
                "2. **Reach Out**: Talk to someone you trust, even if it's just to say you're struggling\n"
                "3. **Professional Help**: A therapist or counselor can provide evidence-based treatment\n"
                "4. **Crisis Resources**: If you're in crisis, contact a helpline immediately\n\n"
                "Please consider speaking with a mental health professional. You deserve support.",
                
                "Depression can make everything feel heavy and hopeless, but these feelings are temporary. "
                "You're brave for reaching out. Have you considered talking to a therapist or counselor?"
            ],
            
            "stress": [
                "Stress is a natural response, but chronic stress can affect your wellbeing. Let's work on managing it:\n\n"
                "**Immediate Relief:**\n"
                "- Take a 5-minute break to breathe deeply\n"
                "- Go for a short walk if possible\n"
                "- Write down what's stressing you\n\n"
                "**Long-term Strategies:**\n"
                "- Prioritize and delegate tasks\n"
                "- Set boundaries between work and personal life\n"
                "- Regular exercise and sleep schedule\n"
                "- Mindfulness or meditation practice\n\n"
                "If stress is overwhelming, a counselor can help you develop personalized coping strategies.",
                
                "It sounds like you're dealing with a lot right now. Stress management is a skill we can develop. "
                "What's your biggest source of stress currently?"
            ],
            
            "suicide_watch": [
                "⚠️ **URGENT**: If you're having thoughts of suicide, please reach out for help immediately:\n\n"
                "🆘 **Crisis Resources:**\n"
                "- **988 Suicide & Crisis Lifeline**: Call/Text 988 (USA)\n"
                "- **Crisis Text Line**: Text HOME to 741741\n"
                "- **International Association for Suicide Prevention**: https://www.iasp.info/resources/Crisis_Centres/\n"
                "- **Emergency Services**: Call 911 or go to nearest ER\n\n"
                "Your life has value. These feelings are temporary, even if they don't feel that way right now. "
                "Please reach out to a professional who can help you through this crisis.\n\n"
                "You are not alone. Help is available 24/7.",
                
                "I'm very concerned about you. Please contact a crisis helpline immediately. "
                "Your life matters, and trained professionals are available right now to help you."
            ],
            
            "ptsd": [
                "PTSD is a real and treatable condition. What you're experiencing is a normal response to trauma. "
                "Here's what can help:\n\n"
                "1. **Professional Treatment**: Evidence-based therapies like EMDR and CPT are very effective\n"
                "2. **Grounding Techniques**: When triggered, focus on your present surroundings\n"
                "3. **Self-Care**: Maintain routine, exercise, and healthy sleep habits\n"
                "4. **Support Network**: Connect with others who understand\n\n"
                "Healing from trauma takes time, but recovery is possible. Please consider working with a "
                "trauma-informed therapist.",
                
                "Trauma responses are not your fault. Your reactions make sense given what you've been through. "
                "Have you been able to connect with a trauma specialist?"
            ],
            
            "bipolar": [
                "Managing bipolar disorder requires consistent care and support. Here are key strategies:\n\n"
                "1. **Medication Compliance**: Work closely with a psychiatrist\n"
                "2. **Mood Tracking**: Keep a journal to identify patterns and triggers\n"
                "3. **Sleep Schedule**: Maintain consistent sleep/wake times\n"
                "4. **Stress Management**: Avoid excessive stress when possible\n"
                "5. **Support System**: Join a support group or therapy\n\n"
                "If you're experiencing severe mood swings, please contact your healthcare provider.",
                
                "Bipolar disorder is manageable with the right treatment plan. Are you currently working "
                "with a mental health professional?"
            ],
            
            "general_mental_health": [
                "Thank you for sharing. Taking care of your mental health is important. Here are some general strategies:\n\n"
                "1. **Self-Care Basics**: Regular sleep, nutritious food, physical activity\n"
                "2. **Social Connection**: Reach out to friends, family, or support groups\n"
                "3. **Mindfulness**: Try meditation, journaling, or relaxation techniques\n"
                "4. **Professional Support**: Consider therapy even for general wellness\n"
                "5. **Limit Stress**: Set boundaries and practice saying no\n\n"
                "Remember, seeking help is a sign of strength, not weakness.",
                
                "Mental health is just as important as physical health. What specific areas would you "
                "like support with?"
            ]
        }
        
        # Return templates or fallback
        return templates.get(concern, templates["general_mental_health"])
    
    def _get_fallback_response(self) -> str:
        """Fallback response when something goes wrong."""
        return (
            "I'm here to listen and support you. While I can provide general guidance, "
            "I strongly encourage you to speak with a licensed mental health professional "
            "who can provide personalized care. \n\n"
            "**Resources:**\n"
            "- National Alliance on Mental Illness (NAMI): 1-800-950-NAMI\n"
            "- Substance Abuse and Mental Health Services (SAMHSA): 1-800-662-4357\n"
            "- Crisis Text Line: Text HOME to 741741\n\n"
            "Your mental health matters. Please reach out for professional support."
        )
    
    def get_crisis_assessment(self, text: str) -> Dict[str, any]:
        """
        Assess if the user is in crisis and needs immediate help.
        
        Args:
            text: User's input text
            
        Returns:
            Dictionary with crisis assessment
        """
        crisis_keywords = [
            "suicide", "kill myself", "end it all", "don't want to live",
            "better off dead", "harm myself", "no reason to live",
            "take my life", "die", "overdose"
        ]
        
        text_lower = text.lower()
        crisis_indicators = sum(1 for keyword in crisis_keywords if keyword in text_lower)
        
        mental_state = self.analyze_mental_state(text)
        suicide_risk = mental_state.get("suicide_watch", 0.0)
        
        is_crisis = crisis_indicators > 0 or suicide_risk > 0.6
        
        return {
            "is_crisis": is_crisis,
            "suicide_risk_score": suicide_risk,
            "crisis_indicators_found": crisis_indicators,
            "recommendation": "IMMEDIATE_HELP" if is_crisis else "STANDARD_SUPPORT"
        }
    
    def process_query(self, user_input: str) -> Dict[str, any]:
        """
        Process a user query and return comprehensive response.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with analysis and response
        """
        try:
            # Crisis assessment
            crisis_assessment = self.get_crisis_assessment(user_input)
            
            # Mental state analysis
            mental_state = self.analyze_mental_state(user_input)
            
            # Generate response
            response = self.generate_supportive_response(user_input, mental_state)
            
            # Prepare result
            result = {
                "response": response,
                "mental_state_analysis": mental_state,
                "primary_concern": max(mental_state.items(), key=lambda x: x[1])[0],
                "concern_confidence": max(mental_state.values()),
                "crisis_assessment": crisis_assessment,
                "recommendation": (
                    "Please seek immediate professional help if you're in crisis. "
                    "Otherwise, consider speaking with a licensed therapist or counselor."
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": self._get_fallback_response(),
                "error": str(e)
            }


# Example usage
if __name__ == "__main__":
    assistant = PsychologyAssistant()
    
    # Test queries
    test_queries = [
        "I've been feeling really anxious lately and can't sleep",
        "I feel so sad all the time, nothing makes me happy anymore",
        "I'm so stressed with work and family responsibilities"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"User: {query}")
        print(f"{'='*80}")
        result = assistant.process_query(query)
        print(f"\nAnalysis: {result['mental_state_analysis']}")
        print(f"Primary Concern: {result['primary_concern']}")
        print(f"\nResponse:\n{result['response']}")
