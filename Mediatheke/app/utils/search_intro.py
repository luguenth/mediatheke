import cv2
import numpy as np
from sklearn.cluster import KMeans

# Function to extract features from a single frame
def extract_features(frame):
    # Initialize SIFT detector
    sift = cv2.SIFT_create()
    
    # Convert frame to grayscale (SIFT requires grayscale images)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect SIFT features
    keypoints, descriptors = sift.detectAndCompute(gray_frame, None)
    
    return descriptors

# Aggregating features for a scene
def aggregate_features(scene_frames):
    # Placeholder for aggregated features, you can use more complex techniques
    aggregated_features = []
    
    # We aggregate features from each frame in the scene to create a scene's feature
    for frame in scene_frames:
        frame_features = extract_features(frame)
        
        # Aggregation (e.g., averaging, although more complex methods can be used)
        if frame_features is not None:
            aggregated_features.append(frame_features)
    
    # Example: simple averaging
    return sum(aggregated_features) / len(aggregated_features)

# Video stream URLs
url1 = 'https://pdvideosdaserste-a.akamaihd.net/de/2018/10/01/bbf4b89c-9a7c-4f33-ade5-2e12d36df44d/JOB_350137_sendeton_640x360-50p-1200kbit.mp4'
url2 = 'https://pdvideosdaserste-a.akamaihd.net/de/2018/10/01/2e9d7140-7ff6-49ad-984b-cc0ac9289815/JOB_350134_sendeton_640x360-50p-1200kbit.mp4'

def read_and_cluster_video(url, num_clusters=3):
    # Read video
    video_cap = cv2.VideoCapture(url)
    scene_features = []
    
    while True:
        ret, frame = video_cap.read()
        if not ret:
            break
            
        features = extract_features(frame)
        if features is not None:
            scene_features.append(features)
    
    video_cap.release()
    
    # We cluster scenes, assuming 3 common types (intro, outro, recap)
    # More sophisticated approaches can also be used
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(np.vstack(scene_features))
    
    return kmeans.cluster_centers_

# Find similar scenes across two videos
def find_similar_scenes(url1, url2, num_clusters=3):
    centers1 = read_and_cluster_video(url1, num_clusters)
    centers2 = read_and_cluster_video(url2, num_clusters)
    
    # Comparing using Euclidean distance, other metrics like cosine similarity can be used
    similarities = {}
    for i, center1 in enumerate(centers1):
        for j, center2 in enumerate(centers2):
            dist = np.linalg.norm(center1 - center2)
            similarities[(i, j)] = dist
            
    # Sort to find the most similar scene clusters
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1])
    
    return sorted_similarities

# Example usage
similarities = find_similar_scenes(url1, url2)
print("Most similar scene clusters are:", similarities[0])
