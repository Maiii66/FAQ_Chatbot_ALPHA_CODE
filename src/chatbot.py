import pandas as pd
from preprocessing import TextPreprocessor
from similarity import SimilarityMatcher

class FAQChatbot:
    """
    Main Chatbot class that orchestrates preprocessing and matching
    """
    
    def __init__(self, faq_file):
        """
        Initialize chatbot with FAQ data
        
        Args:
            faq_file (str): Path to CSV file with FAQs
        """
        print("📚 Loading FAQs...")
        
        # Load FAQ data
        self.faqs = pd.read_csv(faq_file)
        
        print(f"✅ Loaded {len(self.faqs)} FAQs")
        
        # Initialize text preprocessor
        print("🧹 Initializing text preprocessor...")
        self.preprocessor = TextPreprocessor()
        
        # Preprocess all FAQ questions
        self.faqs['processed_question'] = self.faqs['question'].apply(
            self.preprocessor.clean_text
        )
        
        # Initialize similarity matcher
        print("🔍 Initializing similarity matcher...")
        self.matcher = SimilarityMatcher(self.faqs)
        
        print("🤖 Chatbot ready!\n")
    
    def get_response(self, user_question, top_k=1, threshold=0.3):
        """
        Get chatbot response to user question
        
        Args:
            user_question (str): Raw user question
            top_k (int): Number of results to consider
            threshold (float): Minimum similarity threshold
            
        Returns:
            dict: Response with answer, confidence, and status
        """
        # Preprocess user question
        processed_question = self.preprocessor.clean_text(user_question)
        
        # Find matches
        matches = self.matcher.find_best_match(
            processed_question,
            top_k=top_k,
            threshold=threshold
        )
        
        # Prepare response
        if matches:
            best_match = matches[0]
            return {
                'answer': best_match['answer'],
                'confidence': f"{best_match['similarity']*100:.1f}%",
                'category': best_match['category'],
                'status': 'success'
            }
        else:
            return {
                'answer': "Sorry, I couldn't find a matching answer. Please contact support or ask another question.",
                'confidence': '0%',
                'category': 'unknown',
                'status': 'no_match'
            }


# Test the chatbot
if __name__ == "__main__":
    # Initialize chatbot
    chatbot = FAQChatbot('data/faqs.csv')
    
    # Test conversations
    test_questions = [
        "How do I reset my password?",
        "What are the gym timings?",
        "Can I freeze my membership?",
        "Do you have a sauna?",
        "What's your email address?",  # This won't match (testing no_match)
    ]
    
    print("=" * 60)
    print("💬 CHATBOT TEST CONVERSATION")
    print("=" * 60)
    
    for question in test_questions:
        print(f"\n👤 User: {question}")
        
        response = chatbot.get_response(question, threshold=0.35)
        
        print(f"🤖 Bot: {response['answer']}")
        print(f"📊 Confidence: {response['confidence']} | Category: {response['category']}")
        print("-" * 60) 