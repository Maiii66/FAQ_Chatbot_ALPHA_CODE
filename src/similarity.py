import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import sys
from collections import Counter

try:
    from .utils import ensure_utf8_console
except ImportError:
    from utils import ensure_utf8_console

# Fix Windows console crash when running this module directly (emoji prints)
ensure_utf8_console()


class SimilarityMatcher:
    """
    Finds the most similar FAQs using improved matching logic
    """
    
    def __init__(self, faqs_dataframe):
        """
        Initialize the matcher with FAQ data
        
        Args:
            faqs_dataframe (pd.DataFrame): DataFrame with 'processed_question' column
        """
        self.faqs = faqs_dataframe
        self.vectorizer = TfidfVectorizer(analyzer='word', lowercase=True, max_features=1000)
        
        # Document frequency of tokens across all answers, used to detect and
        # strip "hub" words (members, trainers, plans, ...) that appear in the
        # long About-style answers and would otherwise hijack every query.
        self._answer_df = Counter()
        if 'processed_answer' in self.faqs.columns:
            for ans in self.faqs['processed_answer'].astype(str):
                for tok in set(ans.split()):
                    self._answer_df[tok] += 1
        
        # Match text = curated keywords when available, else hub-filtered answers.
        question_text = self.faqs['processed_question'].astype(str)
        if 'processed_keywords' in self.faqs.columns:
            extra_text = self.faqs['processed_keywords'].astype(str)
        elif 'processed_answer' in self.faqs.columns:
            extra_text = self.faqs['processed_answer'].astype(str).apply(
                self._strip_hub_tokens
            )
        else:
            extra_text = question_text
        
        self.vectorizer.fit(question_text + ' ' + extra_text)
        self.question_vectors = self.vectorizer.transform(question_text)
        self.keyword_vectors = self.vectorizer.transform(extra_text)
        
        # Per-FAQ vocabulary (question + match text) used to gate matches by
        # token coverage so a FAQ must genuinely answer the query. This stops a
        # shared generic keyword (e.g. "discount" in corporate/membership vs a
        # "student discount" query the FAQ never answers) from hijacking intent.
        self._match_tokens = [
            set(q.split()) | set(e.split())
            for q, e in zip(question_text, extra_text)
        ]
    
    def _strip_hub_tokens(self, text, max_df=4):
        """Remove tokens that occur in many FAQ answers so broad answers don't
        out-score the FAQ that actually answers the question."""
        tokens = [t for t in text.split() if self._answer_df.get(t, 0) <= max_df]
        return ' '.join(tokens)
    
    def find_best_match(self, user_question, top_k=3, threshold=0.25):
        """
        Find best matching FAQ with IMPROVED logic to prioritize detailed answers
        
        Args:
            user_question (str): Preprocessed user question
            top_k (int): Number of top results to return (default: 3)
            threshold (float): Minimum similarity score (0-1) (default: 0.25)
            
        Returns:
            list: List of matching FAQs with similarity scores
        """
        # Convert user question to vector
        user_vector = self.vectorizer.transform([user_question])
        
        # Token-coverage gate: keep only FAQs whose vocabulary covers more than
        # half of the query's meaningful tokens. TF-IDF drops out-of-vocabulary
        # words, so without this "student discount" is indistinguishable from
        # "discount" (the vectorizer sees only the shared token). With it, a
        # two-word query must genuinely be addressed by the answer.
        q_tokens = set(user_question.split())
        eligible = [
            i for i, toks in enumerate(self._match_tokens)
            if q_tokens and len(q_tokens & toks) * 2 > len(q_tokens)
        ]
        
        # Score against FAQ questions (intent) and keywords/answers separately,
        # then take the best of the two so answer-only keywords still match.
        question_similarities = cosine_similarity(user_vector, self.question_vectors)[0]
        keyword_similarities = cosine_similarity(user_vector, self.keyword_vectors)[0]
        similarities = np.maximum(question_similarities, keyword_similarities)
        
        # Exclude FAQs that fail the coverage gate
        mask = np.zeros(len(similarities), dtype=bool)
        mask[eligible] = True
        similarities = np.where(mask, similarities, -1.0)
        
        # Get indices of top K most similar FAQs
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results that meet the threshold (no artificial boost; the old
        # score*1.1 heuristic could not reorder and only distorted confidence)
        results = []
        for idx in top_indices:
            similarity_score = float(similarities[idx])
            if similarity_score >= threshold:
                results.append({
                    'index': int(idx),
                    'question': self.faqs.iloc[idx]['question'],
                    'answer': self.faqs.iloc[idx]['answer'],
                    'category': self.faqs.iloc[idx]['category'],
                    'similarity': similarity_score
                })
        
        return results


# Test the similarity matcher
if __name__ == "__main__":
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    
    faqs = pd.read_csv(Path(__file__).resolve().parent.parent / 'data' / 'faqs.csv')
    
    try:
        from .preprocessing import TextPreprocessor
    except ImportError:
        from preprocessing import TextPreprocessor
    
    processor = TextPreprocessor()
    faqs['processed_question'] = faqs['question'].apply(processor.clean_text)
    faqs['processed_answer'] = faqs['answer'].apply(processor.clean_text)
    if 'keywords' in faqs.columns:
        faqs['processed_keywords'] = faqs['keywords'].fillna('').apply(processor.clean_text)
    
    matcher = SimilarityMatcher(faqs)
    
    test_questions = [
        "hey mate",
        "gym price",
        "gym timings",
    ]
    
    print("🔍 SIMILARITY MATCHING TESTS:\n")
    for test_q in test_questions:
        processed_q = processor.clean_text(test_q)
        matches = matcher.find_best_match(processed_q, top_k=2, threshold=0.2)
        
        print(f"User: {test_q}")
        print(f"Processed: {processed_q}\n")
        
        if matches:
            for i, match in enumerate(matches, 1):
                print(f"  Match {i}:")
                print(f"    FAQ: {match['question']}")
                print(f"    Similarity: {match['similarity']*100:.1f}%")
        print()