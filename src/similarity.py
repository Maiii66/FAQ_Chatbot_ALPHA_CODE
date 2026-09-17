import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class SimilarityMatcher:
    """
    Finds the most similar FAQs to a user question using Cosine Similarity
    """
    
    def __init__(self, faqs_dataframe):
        """
        Initialize the matcher with FAQ data
        
        Args:
            faqs_dataframe (pd.DataFrame): DataFrame with 'processed_question' column
        """
        self.faqs = faqs_dataframe
        self.vectorizer = TfidfVectorizer(analyzer='word', lowercase=True)
        
        # Create vectors from all FAQ questions
        self.faq_vectors = self.vectorizer.fit_transform(
            self.faqs['processed_question'].astype(str)
        )
    
    def find_best_match(self, user_question, top_k=3, threshold=0.5):
        """
        Find the best matching FAQ(s) for a user question
        
        Args:
            user_question (str): Preprocessed user question
            top_k (int): Number of top results to return (default: 3)
            threshold (float): Minimum similarity score (0-1) (default: 0.5)
            
        Returns:
            list: List of matching FAQs with similarity scores
        """
        # Convert user question to vector
        user_vector = self.vectorizer.transform([user_question])
        
        # Calculate cosine similarity with all FAQs
        similarities = cosine_similarity(user_vector, self.faq_vectors)[0]
        
        # Get indices of top K most similar FAQs
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        results = []
        for idx in top_indices:
            if similarities[idx] >= threshold:
                results.append({
                    'index': int(idx),
                    'question': self.faqs.iloc[idx]['question'],
                    'answer': self.faqs.iloc[idx]['answer'],
                    'category': self.faqs.iloc[idx]['category'],
                    'similarity': float(similarities[idx])
                })
        
        return results


# Test the similarity matcher
if __name__ == "__main__":
    # Load FAQs
    faqs = pd.read_csv('data/faqs.csv')
    
    # Simulate preprocessing (for testing)
    from preprocessing import TextPreprocessor
    processor = TextPreprocessor()
    faqs['processed_question'] = faqs['question'].apply(processor.clean_text)
    
    # Create matcher
    matcher = SimilarityMatcher(faqs)
    
    # Test cases
    test_questions = [
        "How do I reset my password?",
        "What's your gym timing?",
        "Can I cancel my membership?"
    ]
    
    print("🔍 SIMILARITY MATCHING TESTS:\n")
    for test_q in test_questions:
        processed_q = processor.clean_text(test_q)
        matches = matcher.find_best_match(processed_q, top_k=2, threshold=0.3)
        
        print(f"User Question: {test_q}")
        print(f"Processed: {processed_q}\n")
        
        if matches:
            for i, match in enumerate(matches, 1):
                print(f"  Match {i}:")
                print(f"    FAQ: {match['question']}")
                print(f"    Answer: {match['answer'][:60]}...")
                print(f"    Similarity: {match['similarity']*100:.1f}%")
        else:
            print("  No matches found!")
        
        print()