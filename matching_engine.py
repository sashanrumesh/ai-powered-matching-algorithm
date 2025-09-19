# matching_engine.py
import random
import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import math

class MatchingEngine:
    def __init__(self, users_path='fake_users.csv', events_path='fake_events.csv'):
        self.users_df = pd.read_csv(users_path)
        # Convert string of hobbies list to actual list
        self.users_df['hobbies'] = self.users_df['hobbies'].apply(lambda x: x.strip("[]").replace("'", "").split(", "))
        self.events_df = pd.read_csv(events_path)
        self.mlb = MultiLabelBinarizer()
        self.hobby_matrix = self.mlb.fit_transform(self.users_df['hobbies'])
        self.user_clusters = None
        self._cluster_users()

    def _cluster_users(self):
        # Create features for clustering: age, location, hobbies
        cluster_features = pd.get_dummies(self.users_df[['age', 'location_lat', 'location_lon']])
        cluster_features = pd.concat([cluster_features, pd.DataFrame(self.hobby_matrix, columns=self.mlb.classes_)], axis=1)

        # Use K-Means to cluster users into 5 groups
        kmeans = KMeans(n_clusters=5, random_state=42)
        self.user_clusters = kmeans.fit_predict(cluster_features)
        self.users_df['cluster'] = self.user_clusters

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        # Simple approximation for demo purposes
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)

    def calculate_user_score(self, target_user_id, potential_user_id):
        target_user = self.users_df.iloc[target_user_id]
        potential_user = self.users_df.iloc[potential_user_id]

        # 1. Age Range Filter (Client Requirement #1)
        # Let's assume the target user's age prefs are their age ±5 years
        min_age, max_age = target_user['age'] - 5, target_user['age'] + 5
        if not (min_age <= potential_user['age'] <= max_age):
            return 0  # Excluded by hard filter

        # 2. Availability Filter (Client Requirement #2)
        # For this demo, let's just use 'is_online' as a proxy for "active now"
        if not potential_user['is_online']:
            return 0  # Not active now

        # If filters are passed, calculate weighted hybrid score
        scores = {}

        # 3. Hobby Similarity (40%)
        hobbies_target = set(target_user['hobbies'])
        hobbies_potential = set(potential_user['hobbies'])
        hobby_jaccard = len(hobbies_target.intersection(hobbies_potential)) / len(hobbies_target.union(hobbies_potential))
        scores['hobby_similarity'] = hobby_jaccard * 0.4

        # 4. Location Proximity (30%)
        dist = self._calculate_distance(
            target_user['location_lat'], target_user['location_lon'],
            potential_user['location_lat'], potential_user['location_lon']
        )
        # Exponential decay: score drops as distance increases
        location_score = math.exp(-dist * 5)  # Adjust the multiplier (5) to change decay rate
        scores['location_proximity'] = location_score * 0.3

        # 5. Demographics - Age Similarity (20%)
        age_diff = abs(target_user['age'] - potential_user['age'])
        # Gaussian weighting: score is 1 if same age, drops off
        age_score = math.exp(-(age_diff ** 2) / 100.)  # Adjust denominator for wider/narrower peak
        scores['demographics'] = age_score * 0.2

        # 6. Behavioural Signals (10%) - FAKE THIS for demo. Assume all users have good behaviour.
        behaviour_score = 0.8 + (random.random() * 0.2)  # Random score between 0.8-1.0
        scores['behavioural'] = behaviour_score * 0.1

        # Calculate total score
        total_score = sum(scores.values())
        return total_score

    def get_user_matches(self, target_user_id, top_n=10):
        target_user_id = int(target_user_id)
        scores = []
        for user_id in self.users_df.index:
            if user_id == target_user_id:
                continue  # Skip self
            score = self.calculate_user_score(target_user_id, user_id)
            if score > 0:  # Only include users who passed the filters
                scores.append((user_id, score))

        # Sort by score descending and get top N
        scores.sort(key=lambda x: x[1], reverse=True)
        top_matches = scores[:top_n]

        # Prepare the result with user details
        results = []
        for user_id, score in top_matches:
            user = self.users_df.iloc[user_id].to_dict()
            user['match_score'] = score
            results.append(user)
        return results

    def get_event_matches(self, target_user_id, top_n=5):
        target_user = self.users_df.iloc[int(target_user_id)]
        user_cluster = target_user['cluster']
        # Find events related to the user's cluster's hobbies
        # Simple version: find events whose hobby is one of the user's top hobbies
        user_hobbies = set(target_user['hobbies'])
        event_scores = []
        for _, event in self.events_df.iterrows():
            if event['hobby'] in user_hobbies:
                score = 1.0
            else:
                score = 0.1
            event_scores.append((event['event_id'], score))

        event_scores.sort(key=lambda x: x[1], reverse=True)
        top_events = event_scores[:top_n]
        results = []
        for event_id, score in top_events:
            event = self.events_df[self.events_df['event_id'] == event_id].iloc[0].to_dict()
            event['match_score'] = score
            results.append(event)
        return results

# For quick testing
if __name__ == '__main__':
    engine = MatchingEngine()
    print("Testing match for user 0:")
    matches = engine.get_user_matches(0, top_n=3)
    for match in matches:
        print(f"User {match['user_id']} ({match['name']}): Score {match['match_score']:.2f}, Hobbies: {match['hobbies']}")