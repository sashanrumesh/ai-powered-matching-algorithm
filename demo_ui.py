# demo_ui.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# API base URL
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Kumele Demo", layout="wide")
st.title("Kumele Matching Algorithm Demo 🎯")
st.markdown("Swipe right to like, left to pass. This demo uses fake data and ML clustering.")

# Fetch all users
@st.cache_data
def load_users():
    response = requests.get(f"{API_BASE}/users/")
    return response.json()

users = load_users()
user_df = pd.DataFrame(users)

# Select a user to test with
target_user_id = st.sidebar.selectbox("Choose Your User Profile", options=user_df['user_id'], format_func=lambda x: f"User {x}: {user_df.iloc[x]['name']} (Age: {user_df.iloc[x]['age']})")

if st.sidebar.button("Find Matches for Me!"):
    with st.spinner("Finding your perfect match..."):
        # Call our API
        response = requests.get(f"{API_BASE}/match/users/{target_user_id}", params={"top_n": 15})
        if response.status_code == 200:
            data = response.json()
            matches = data['matches']
            st.session_state['matches'] = matches
            st.session_state['current_match_index'] = 0
        else:
            st.error("Failed to fetch matches.")

# Display the current match in a Tinder-like card
if 'matches' in st.session_state and st.session_state['matches']:
    current_index = st.session_state['current_match_index']
    if current_index < len(st.session_state['matches']):
        match = st.session_state['matches'][current_index]
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            st.subheader(f"{match['name']}")
            st.write(f"**Age:** {match['age']}")
            st.write(f"**Hobbies:** {', '.join(match['hobbies'])}")
            st.write(f"**Location:** ({match['location_lat']:.2f}, {match['location_lon']:.2f})")
            st.write(f"**Online Now:** {'Yes' if match['is_online'] else 'No'}")
            st.metric("Match Score", f"{match['match_score']:.2%}")

            # Create a map for the match - FIXED THIS PART
            map_data = [
                {'lat': user_df.iloc[target_user_id]['location_lat'], 'lon': user_df.iloc[target_user_id]['location_lon'], 'type': 'You'},
                {'lat': match['location_lat'], 'lon': match['location_lon'], 'type': 'Them'}
            ]
            map_df = pd.DataFrame(map_data)
            
            fig = px.scatter_mapbox(map_df, lat="lat", lon="lon", color="type", zoom=10, height=300)
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)

            # Swipe buttons
            col_left, col_right = st.columns(2)
            with col_left:
                if st.button("👎 Pass", use_container_width=True):
                    st.session_state['current_match_index'] += 1
                    st.rerun()
            with col_right:
                if st.button("👍 Like", use_container_width=True):
                    st.success(f"You liked {match['name']}!")
                    st.session_state['current_match_index'] += 1
                    st.rerun()
    else:
        st.info("You've seen all your top matches! Try a different user.")

# Show the user clusters (the ML part)
st.sidebar.subheader("User Clusters (ML Visualization)")
# Convert cluster to string for better visualization
user_df['cluster_str'] = user_df['cluster'].astype(str)
fig = px.scatter(user_df, x='location_lon', y='location_lat', color='cluster_str', hover_data=['name', 'age', 'hobbies'])
fig.update_layout(title="Users Clustered by Age, Location, and Hobbies (K-Means)")
st.sidebar.plotly_chart(fig, use_container_width=True)