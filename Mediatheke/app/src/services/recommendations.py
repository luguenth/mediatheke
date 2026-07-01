from fastapi import FastAPI, Depends
from sklearn.feature_extraction.text import TfidfVectorizer
from ..mediaitem import crud
from ...core.db.database import get_new_db_session

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
        if cls._instance is None:
            cls._instance = super(RecommendationEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def load(self):
        """Load data in a background worker. Returns True on success."""
        try:
            self._load_data()
            return True
        except Exception as e:
            print(f"Failed to load recommendation engine data: {e}")
            return False

    def _load_data(self):
        db = get_new_db_session()
        print("Getting media items for recommendation engine")
        media_items = crud.get_unlimited_media_items(db)
        self.item_ids = [item.id for item in media_items]
        self.item_durations = [item.duration for item in media_items]
        texts = [
            item.title * 1 + " " +
            item.description * 1
            for item in media_items]
        self.vectorizer = TfidfVectorizer(stop_words=german_stop_words)
        self.X = self.vectorizer.fit_transform(texts)
        print("Finished loading data for recommendation engine")

    def get_recommendations(self, video_id, **common_params):
        if not hasattr(self, 'X') or self.X is None:
            return []
        try:
            idx = self.item_ids.index(video_id)
        except ValueError:
            return []

        cosine_similarities = linear_kernel(self.X[idx], self.X).flatten()

        # Sort the videos by similarity score
        related_docs_indices = cosine_similarities.argsort()[::-1]

        # Filter out recommendations with the same duration until we hit the limit
        seen_durations = set()
        recommended_ids = []
        for index in related_docs_indices:
            # Skip the current video itself
            if index == idx:
                continue

            if len(recommended_ids) >= common_params["limit"]:
                break
            if self.item_durations[index] not in seen_durations:
                recommended_ids.append(self.item_ids[index])
                seen_durations.add(self.item_durations[index])

        if not recommended_ids:
            return []

        db = get_new_db_session()
        return crud.get_all_media_items_by_ids(db, ",".join(map(str, recommended_ids)), limit=common_params["limit"])
    
    def get_recommendations_for_text(self, query_text, **common_params):
        if not hasattr(self, 'X') or self.X is None:
            return []
        # Convert query text into a vector
        query_vector = self.vectorizer.transform([query_text])

        # Compute cosine similarity with all media items
        cosine_similarities = linear_kernel(query_vector, self.X).flatten()

        # Sort the videos by similarity score
        related_docs_indices = cosine_similarities.argsort()[::-1]

        # Filter out recommendations with the same duration until we hit the limit
        seen_durations = set()
        recommended_ids = []
        for index in related_docs_indices:
            if len(recommended_ids) >= common_params["limit"]:
                break
            if self.item_durations[index] not in seen_durations:
                recommended_ids.append(self.item_ids[index])
                seen_durations.add(self.item_durations[index])

        if not recommended_ids:
            return []

        db = get_new_db_session()
        recommendations = crud.get_all_media_items_by_ids(db, ",".join(map(str, recommended_ids)), limit=common_params["limit"])
        print("Recommendations for query", query_text, ":", recommendations)
        return recommendations
    
def get_recommendation_engine():
    global _rec_engine_instance

    if _rec_engine_instance is None:
        _rec_engine_instance = RecommendationEngine()
    return _rec_engine_instance
