from fastapi import FastAPI, Depends
from sklearn.feature_extraction.text import TfidfVectorizer
from ..mediaitem import crud
from ...core.db.database import get_new_db_session
from ..mediaitem.model import MediaItem
from sklearn.metrics.pairwise import linear_kernel
import nltk
from nltk.corpus import stopwords

# Download stopwords only once
nltk.download('stopwords')
german_stop_words = stopwords.words('german')


# Global variable to hold the singleton instance
_rec_engine_instance = None

class RecommendationEngine:
    _instance = None  # Class variable to hold the singleton instance

    def __new__(cls):
        # This ensures that only one instance of RecommendationEngine is created
        if cls._instance is None:
            cls._instance = super(RecommendationEngine, cls).__new__(cls)
            # Initialize data once after the instance is created
            cls._instance._load_data()
        return cls._instance

    def __init__(self):
        # Since the __new__ method initializes the data, the __init__ method should avoid reinitializing.
        pass

    def _load_data(self):
        db = get_new_db_session()
        print("Getting media items for recommendation engine")
        self.media_items = crud.get_unlimited_media_items(db)
        texts = [\
                #item.topic * 1 + " " + \
                item.title * 1 + " " + \
                item.description * 1 \
            for item in self.media_items]        
        self.vectorizer = TfidfVectorizer(stop_words=german_stop_words)
        self.X = self.vectorizer.fit_transform(texts)
        print("Finished loading data for recommendation engine")

    def get_recommendations(self, video_id, **common_params):
        idx = None
        for i, item in enumerate(self.media_items):
            if item.id == video_id:
                idx = i
                break

        if idx is None:
            return []

        cosine_similarities = linear_kernel(self.X[idx], self.X).flatten()

        # Sort the videos by similarity score
        related_docs_indices = cosine_similarities.argsort()[::-1]

        # Filter out recommendations with the same duration until you have 10 unique durations
        seen_durations = set()
        recommendations = []
        for index in related_docs_indices:
            # Skip the current video itself
            if index == idx:
                continue

            if len(recommendations) >= common_params["limit"]:
                break
            if self.media_items[index].duration not in seen_durations:
                recommendations.append(self.media_items[index])
                seen_durations.add(self.media_items[index].duration)

        return recommendations
    
    def get_recommendations_for_text(self, query_text, **common_params):
        # Convert query text into a vector
        query_vector = self.vectorizer.transform([query_text])

        # Compute cosine similarity with all media items
        cosine_similarities = linear_kernel(query_vector, self.X).flatten()

        # Sort the videos by similarity score
        related_docs_indices = cosine_similarities.argsort()[::-1]

        # Filter out recommendations with the same duration until you have 10 unique durations
        seen_durations = set()
        recommendations = []
        for index in related_docs_indices:
            if len(recommendations) >= common_params["limit"]:
                break
            if self.media_items[index].duration not in seen_durations:
                recommendations.append(self.media_items[index])
                seen_durations.add(self.media_items[index].duration)

        print("Recommendations for query", query_text, ":", recommendations)
        return recommendations
    
def get_recommendation_engine():
    global _rec_engine_instance

    if _rec_engine_instance is None:
        _rec_engine_instance = RecommendationEngine()
    return _rec_engine_instance