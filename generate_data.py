# generate_data.py
import pandas as pd
import numpy as np
from faker import Faker
import random

# Install faker if you don't have it: pip install faker
fake = Faker()

# Define a list of common hobbies
ALL_HOBBIES = [
    'hiking', 'coding', 'gaming', 'reading', 'cooking', 'photography',
    'yoga', 'painting', 'music', 'dancing', 'traveling', 'cycling',
    'swimming', 'running', 'chess', 'movies', 'blogging', 'gardening'
]

NUM_USERS = 100  # Let's generate 100 fake users

def generate_fake_users(n):
    users = []
    for i in range(n):
        profile = fake.profile()
        # Generate a random location within a roughly 50km radius
        base_lat, base_lon = 40.7128, -74.0060  # New York coordinates
        lat = base_lat + random.uniform(-0.5, 0.5)
        lon = base_lon + random.uniform(-0.5, 0.5)

        user = {
            'user_id': i,
            'name': profile['name'],
            'age': random.randint(18, 70),
            'location_lat': lat,
            'location_lon': lon,
            # Assign 3-6 random hobbies to each user
            'hobbies': random.sample(ALL_HOBBIES, k=random.randint(3, 6)),
            # 70% chance of being "active now"
            'is_online': random.random() > 0.3,
            # Simulate a schedule (e.g., available on weekends vs weekdays)
            'available_weekends': random.random() > 0.5,
            'available_weekdays': random.random() > 0.5,
        }
        users.append(user)
    return pd.DataFrame(users)

def generate_fake_events(users_df, n_events=20):
    events = []
    for i in range(n_events):
        host = users_df.iloc[random.randint(0, len(users_df)-1)]
        event = {
            'event_id': i,
            'title': fake.sentence(nb_words=4),
            'host_id': host['user_id'],
            'hobby': random.choice(ALL_HOBBIES),  # The main hobby for the event
            'location_lat': host['location_lat'] + random.uniform(-0.1, 0.1),
            'location_lon': host['location_lon'] + random.uniform(-0.1, 0.1),
        }
        events.append(event)
    return pd.DataFrame(events)

if __name__ == '__main__':
    print("Generating fake user data...")
    users_df = generate_fake_users(NUM_USERS)
    users_df.to_csv('fake_users.csv', index=False)
    print(f"Saved {len(users_df)} users to 'fake_users.csv'")

    print("Generating fake event data...")
    events_df = generate_fake_events(users_df)
    events_df.to_csv('fake_events.csv', index=False)
    print(f"Saved {len(events_df)} events to 'fake_events.csv'")

    print("Data generation complete!")