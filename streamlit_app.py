import streamlit as st # Import the Streamlit library for building web applications.
import pandas as pd # Import pandas for data manipulation.
import os # Import os for path manipulation, especially for the CSV file.
from datetime import datetime # Import datetime to record the timestamp of reviews.

# --- CSV File Configuration ---
REVIEWS_CSV_FILE = "reviews.csv" # Define the name of the CSV file to store reviews.

# --- Initialize CSV file if it doesn't exist ---
if not os.path.exists(REVIEWS_CSV_FILE):
    # Create an empty DataFrame with the required columns if the CSV doesn't exist.
    initial_reviews_df = pd.DataFrame(columns=[
        "restaurant_name", "rating", "review_text",
        "reviewer_name", "reviewer_department", "reviewer_designation",
        "timestamp"
    ])
    initial_reviews_df.to_csv(REVIEWS_CSV_FILE, index=False) # Save the empty DataFrame to CSV.

# --- Session State Initialization ---
# Initialize session state to track which restaurant's review form is open.
if 'review_restaurant_name' not in st.session_state:
    st.session_state.review_restaurant_name = None
if 'review_submitted_message' not in st.session_state:
    st.session_state.review_submitted_message = None

# --- Sample Restaurant Data ---
# Create a list of dictionaries, where each dictionary represents a restaurant.
restaurant_data = [
    {
        "Name": "The Dempsey Cookhouse & Bar",
        "Cuisine": "Modern European",
        "Location": "Dempsey Hill",
        "Rating": 4.5,
        "Price Range": "$$$",
        "Description": "Chic restaurant by Jean-Georges Vongerichten, offering a sophisticated dining experience.",
        "Image": "https://placehold.co/600x400/FF5733/FFFFFF?text=Dempsey+Cookhouse" # Placeholder image URL
    },
    {
        "Name": "Odette",
        "Cuisine": "French",
        "Location": "City Hall",
        "Rating": 5.0,
        "Price Range": "$$$$",
        "Description": "Three Michelin-starred modern French restaurant, known for its exquisite tasting menus.",
        "Image": "https://placehold.co/600x400/33FF57/000000?text=Odette" # Placeholder image URL
    },
    {
        "Name": "Burnt Ends",
        "Cuisine": "Australian BBQ",
        "Location": "Outram Park",
        "Rating": 4.7,
        "Price Range": "$$$",
        "Description": "Modern Australian barbecue with an open-concept kitchen and custom-built ovens.",
        "Image": "https://placehold.co/600x400/3357FF/FFFFFF?text=Burnt+Ends" # Placeholder image URL
    },
    {
        "Name": "Candlenut",
        "Cuisine": "Peranakan",
        "Location": "Dempsey Hill",
        "Rating": 4.3,
        "Price Range": "$$",
        "Description": "The world's first Michelin-starred Peranakan restaurant, offering refined Straits-Chinese cuisine.",
        "Image": "https://placehold.co/600x400/FF33A1/FFFFFF?text=Candlenut" # Placeholder image URL
    },
    {
        "Name": "Jumbo Seafood",
        "Cuisine": "Seafood",
        "Location": "Riverside Point",
        "Rating": 4.2,
        "Price Range": "$$",
        "Description": "Famous for its Chili Crab and Black Pepper Crab, a must-visit for seafood lovers.",
        "Image": "https://placehold.co/600x400/A1FF33/000000?text=Jumbo+Seafood" # Placeholder image URL
    },
    {
        "Name": "Tiong Bahru Bakery",
        "Cuisine": "Cafe",
        "Location": "Tiong Bahru",
        "Rating": 4.0,
        "Price Range": "$",
        "Description": "Popular spot for freshly baked pastries, coffee, and a relaxed atmosphere.",
        "Image": "https://placehold.co/600x400/33A1FF/FFFFFF?text=Tiong+Bahru+Bakery" # Placeholder image URL
    },
    {
        "Name": "Newton Food Centre",
        "Cuisine": "Local Hawker",
        "Location": "Newton",
        "Rating": 3.8,
        "Price Range": "$",
        "Description": "An iconic hawker centre offering a wide variety of local Singaporean dishes.",
        "Image": "https://placehold.co/600x400/FFBB33/000000?text=Newton+Food+Centre" # Placeholder image URL
    },
    {
        "Name": "PS.Cafe Harding Road",
        "Cuisine": "Western/Cafe",
        "Location": "Dempsey Hill",
        "Rating": 4.1,
        "Price Range": "$$",
        "Description": "A popular cafe chain known for its truffle fries, relaxed ambiance, and lush surroundings.",
        "Image": "https://placehold.co/600x400/BB33FF/FFFFFF?text=PS.Cafe" # Placeholder image URL
    },
    {
        "Name": "National Kitchen by Violet Oon",
        "Cuisine": "Peranakan",
        "Location": "City Hall",
        "Rating": 4.4,
        "Price Range": "$$$",
        "Description": "Elegant restaurant serving classic Peranakan dishes in a grand setting at the National Gallery.",
        "Image": "https://placehold.co/600x400/33FFBB/000000?text=National+Kitchen" # Placeholder image URL
    },
    {
        "Name": "Les Amis",
        "Cuisine": "French",
        "Location": "Orchard",
        "Rating": 4.9,
        "Price Range": "$$$$",
        "Description": "One of Singapore's oldest independent fine-dining French restaurants, with three Michelin stars.",
        "Image": "https://placehold.co/600x400/FF3333/FFFFFF?text=Les+Amis" # Placeholder image URL
    }
]

# Convert the list of dictionaries into a pandas DataFrame for easier manipulation and display.
df = pd.DataFrame(restaurant_data)

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Singapore Restaurant Guide", # Sets the title that appears in the browser tab.
    layout="wide", # Uses a wide layout for the app, utilizing more screen real estate.
    initial_sidebar_state="expanded" # Makes the sidebar expanded by default.
)

# --- Custom CSS for Styling ---
# Inject custom CSS to enhance the appearance of the Streamlit app.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'); /* Import Inter font */

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif; /* Apply Inter font to all Streamlit elements */
    }

    .main-header {
        font-size: 3em; /* Larger font size for the main header */
        color: #2F4F4F; /* Dark Slate Gray color */
        text-align: center; /* Center align the header text */
        margin-bottom: 30px; /* Add space below the header */
        font-weight: 700; /* Bold font weight */
    }

    .subheader {
        font-size: 1.5em; /* Font size for subheaders */
        color: #4682B4; /* Steel Blue color */
        margin-top: 20px; /* Space above subheaders */
        margin-bottom: 15px; /* Space below subheaders */
        font-weight: 600; /* Semi-bold font weight */
    }

    .stTextInput > div > div > input {
        border-radius: 10px; /* Rounded corners for text input */
        border: 1px solid #ccc; /* Light gray border */
        padding: 8px 12px; /* Padding inside the input field */
    }

    .stSelectbox > div > div {
        border-radius: 10px; /* Rounded corners for selectbox */
        border: 1px solid #ccc; /* Light gray border */
    }

    .stButton > button {
        background-color: #17a589 ; /* Steel green background for buttons */
        color: white; /* White text color */
        border-radius: 10px; /* Rounded corners for buttons */
        padding: 10px 20px; /* Padding inside buttons */
        border: none; /* No border */
        font-weight: 600; /* Semi-bold font weight */
        cursor: pointer; /* Pointer cursor on hover */
        transition: background-color 0.3s ease; /* Smooth transition for background color */
    }

    .stButton > button:hover {
        background-color: #48c9b0; /* Lighter green on hover */
        color: #333
    }

    .restaurant-card {
        background-color: #f9f9f9; /* Light gray background for cards */
        border-radius: 15px; /* More rounded corners for cards */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
        padding: 20px; /* Padding inside cards */
        margin-bottom: 25px; /* Space between cards */
        display: flex; /* Use flexbox for layout within the card */
        flex-direction: column; /* Stack items vertically */
        height: 100%; /* Ensure cards take full height in a grid */
    }

    .restaurant-card img {
        width: 100%; /* Image takes full width of the card */
        height: 200px; /* Fixed height for images */
        object-fit: cover; /* Cover the area, cropping if necessary */
        border-radius: 10px; /* Rounded corners for images */
        margin-bottom: 15px; /* Space below image */
    }

    .restaurant-name {
        font-size: 1.8em; /* Larger font for restaurant name */
        color: #2F4F4F; /* Dark Slate Gray */
        font-weight: 700; /* Bold */
        margin-bottom: 5px; /* Small space below name */
    }

    .restaurant-details {
        font-size: 1.1em; /* Font size for details */
        color: #555; /* Darker gray for details */
        margin-bottom: 8px; /* Space below details */
    }

    .restaurant-description {
        font-size: 0.95em; /* Slightly smaller font for description */
        color: #666; /* Medium gray for description */
        line-height: 1.5; /* Good line height for readability */
        flex-grow: 1; /* Allow description to take available space */
    }

    .st-emotion-cache-1cypcdb { /* Target the main block container for centering */
        padding-top: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True # Allow Streamlit to render raw HTML and CSS.
)

# --- Function to Save Review to CSV ---
def save_review_to_csv(restaurant_name, rating, review_text, reviewer_name, reviewer_department, reviewer_designation):
    """Saves a review to the CSV file."""
    try:
        # Load existing reviews
        reviews_df = pd.read_csv(REVIEWS_CSV_FILE)
        
        # Create a new review record as a DataFrame
        new_review = pd.DataFrame([{
            "restaurant_name": restaurant_name,
            "rating": rating,
            "review_text": review_text,
            "reviewer_name": reviewer_name,
            "reviewer_department": reviewer_department,
            "reviewer_designation": reviewer_designation,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Format timestamp
        }])
        
        # Append the new review to the DataFrame and save back to CSV
        reviews_df = pd.concat([reviews_df, new_review], ignore_index=True)
        reviews_df.to_csv(REVIEWS_CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving review to CSV: {e}")
        return False

# --- Function to Load Reviews from CSV ---
def load_reviews_from_csv(restaurant_name):
    """Loads reviews for a specific restaurant from the CSV file."""
    try:
        reviews_df = pd.read_csv(REVIEWS_CSV_FILE)
        # Filter reviews for the specific restaurant
        restaurant_reviews = reviews_df[reviews_df["restaurant_name"] == restaurant_name]
        # Sort by timestamp in descending order (most recent first)
        restaurant_reviews = restaurant_reviews.sort_values(by="timestamp", ascending=False)
        return restaurant_reviews.to_dict(orient="records") # Return as list of dictionaries
    except FileNotFoundError:
        return [] # Return empty list if file not found
    except Exception as e:
        st.error(f"Error loading reviews from CSV: {e}")
        return []

# --- App Title and Header ---
st.markdown('<h1 class="main-header">🍽️ Singapore Restaurant Guide</h1>', unsafe_allow_html=True) # Display a large, styled main header.
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1em;">Discover the best dining experiences in Singapore!</p>', unsafe_allow_html=True) # A descriptive subtitle.

# --- Sidebar for Filters ---
st.sidebar.header("Filter Restaurants") # Add a header to the sidebar.

# Search bar in the sidebar
search_query = st.sidebar.text_input("Search by Name or Description", "") # Create a text input for searching restaurant names or descriptions.

# Cuisine filter in the sidebar
# Get unique cuisine types from the DataFrame and sort them.
cuisine_options = ["All"] + sorted(df["Cuisine"].unique().tolist())
selected_cuisine = st.sidebar.selectbox("Select Cuisine", cuisine_options) # Create a dropdown (selectbox) for cuisine filtering.

# Location filter in the sidebar
# Get unique location types from the DataFrame and sort them.
location_options = ["All"] + sorted(df["Location"].unique().tolist())
selected_location = st.sidebar.selectbox("Select Location", location_options) # Create a dropdown for location filtering.

# Price Range filter in the sidebar
price_range_options = ["All", "$", "$$", "$$$", "$$$$"] # Define possible price ranges.
selected_price_range = st.sidebar.selectbox("Select Price Range", price_range_options) # Create a dropdown for price range filtering.

# Rating filter in the sidebar
# Create a slider for minimum rating, from 0 to 5 with steps of 0.1.
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)

# --- Apply Filters ---
filtered_df = df.copy() # Create a copy of the original DataFrame to apply filters without modifying the original.

# Filter by search query (case-insensitive)
if search_query: # If a search query is provided
    filtered_df = filtered_df[
        filtered_df["Name"].str.contains(search_query, case=False, na=False) | # Check if name contains query
        filtered_df["Description"].str.contains(search_query, case=False, na=False) # Or if description contains query
    ]

# Filter by cuisine
if selected_cuisine != "All": # If a specific cuisine is selected
    filtered_df = filtered_df[filtered_df["Cuisine"] == selected_cuisine] # Filter DataFrame to show only restaurants of that cuisine.

# Filter by location
if selected_location != "All": # If a specific location is selected
    filtered_df = filtered_df[filtered_df["Location"] == selected_location] # Filter DataFrame by selected location.

# Filter by price range
if selected_price_range != "All": # If a specific price range is selected
    filtered_df = filtered_df[filtered_df["Price Range"] == selected_price_range] # Filter DataFrame by selected price range.

# Filter by minimum rating
filtered_df = filtered_df[filtered_df["Rating"] >= min_rating] # Filter DataFrame to show only restaurants with rating >= min_rating.

# --- Display Results ---
st.markdown('<h2 class="subheader">Available Restaurants</h2>', unsafe_allow_html=True) # Subheader for the results section.

if not filtered_df.empty: # Check if there are any restaurants after filtering
    # Use Streamlit columns to create a responsive grid layout for restaurant cards.
    cols = st.columns(3) # Create 3 columns for displaying restaurant cards.
    col_index = 0 # Initialize column index for distributing cards.

    for index, row in filtered_df.iterrows(): # Iterate over each row (restaurant) in the filtered DataFrame.
        with cols[col_index]: # Place the content in the current column.
            # Use a Streamlit container to apply card styling
            with st.container(border=True): # Using border=True for a default card-like appearance
                st.markdown(f"""
                <div class="restaurant-card">
                    <img src="{row['Image']}" alt="{row['Name']}" onerror="this.onerror=null;this.src='https://placehold.co/600x400/CCCCCC/000000?text=Image+Not+Found';">
                    <div class="restaurant-name">{row['Name']}</div>
                    <div class="restaurant-details">
                        <strong>Cuisine:</strong> {row['Cuisine']}<br>
                        <strong>Location:</strong> {row['Location']}<br>
                        <strong>Rating:</strong> {row['Rating']} ⭐<br>
                        <strong>Price:</strong> {row['Price Range']}
                    </div>
                    <div class="restaurant-description">{row['Description']}</div>
                </div>
                """, unsafe_allow_html=True) # Render each restaurant's details within a styled card using markdown and HTML.

                # Add the "Submit Review" button using Streamlit's native st.button
                if st.button("Submit Review", key=f"submit_review_for_{row['Name']}"):
                    st.session_state.review_restaurant_name = row['Name']
                    st.session_state.review_submitted_message = None # Clear any previous messages
                    st.rerun() # Rerun the app to immediately display the review form

                # Conditional display of the review form for the selected restaurant
                if st.session_state.review_restaurant_name == row['Name']:
                    st.markdown(f"**Review for {row['Name']}:**")
                    reviewer_name = st.text_input("Your Name:", key=f"reviewer_name_{row['Name']}")
                    reviewer_department = st.text_input("Your Department:", key=f"reviewer_dept_{row['Name']}")
                    reviewer_designation = st.text_input("Your Designation:", key=f"reviewer_designation_{row['Name']}")
                    review_rating = st.slider("Rating", 0.0, 5.0, 3.0, 0.5, key=f"review_rating_{row['Name']}")
                    review_text = st.text_area("Your comments:", key=f"review_text_{row['Name']}")
                    
                    # Use columns for submit and cancel buttons to place them side-by-side
                    submit_col, cancel_col = st.columns(2)
                    with submit_col:
                        if st.button("Submit", key=f"submit_review_form_{row['Name']}"):
                            if review_text and reviewer_name: # Ensure review text and name are provided
                                if save_review_to_csv(row['Name'], review_rating, review_text, reviewer_name, reviewer_department, reviewer_designation):
                                    st.session_state.review_submitted_message = f"Thank you for your review of {row['Name']}! Rating: {review_rating} ⭐"
                                    st.session_state.review_restaurant_name = None # Hide the form
                                    st.rerun() # Rerun to show message and hide form
                            else:
                                st.warning("Please provide your name and review comments before submitting.", icon="⚠️")
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_review_form_{row['Name']}"):
                            st.session_state.review_restaurant_name = None # Hide the form
                            st.session_state.review_submitted_message = None # Clear any previous messages
                            st.rerun() # Rerun to hide form

                # Display submission success message if applicable
                if st.session_state.review_submitted_message and st.session_state.review_restaurant_name is None:
                    # Check if the message is for the current restaurant being iterated over
                    if st.session_state.review_submitted_message.startswith(f"Thank you for your review of {row['Name']}"):
                        st.success(st.session_state.review_submitted_message, icon="✅")
                        st.session_state.review_submitted_message = None # Clear message after displaying
                
                # --- Display Past Reviews in an Expander ---
                # The expander will be closed by default
                with st.expander(f"Past Reviews for {row['Name']}"):
                    reviews = load_reviews_from_csv(row['Name'])
                    if reviews:
                        for review in reviews:
                            st.markdown(f"**Rating:** {review.get('rating', 'N/A')} ⭐")
                            st.write(f"**Review:** {review.get('review_text', 'No review text.')}")
                            
                            reviewer_info = []
                            if review.get('reviewer_name'):
                                reviewer_info.append(review['reviewer_name'])
                            if review.get('reviewer_department'):
                                reviewer_info.append(review['reviewer_department'])
                            if review.get('reviewer_designation'):
                                reviewer_info.append(review['reviewer_designation'])
                            
                            reviewer_line = ", ".join(reviewer_info) if reviewer_info else "Anonymous"
                            
                            timestamp = review.get('timestamp', 'N/A')
                            st.caption(f"By {reviewer_line} on {timestamp}")
                            st.markdown("---") # Separator between reviews
                    else:
                        st.info("No reviews yet for this restaurant. Be the first to submit one!")

        col_index = (col_index + 1) % 3 # Move to the next column, cycling back to the first after the third.
else:
    st.info("No restaurants found matching your criteria. Please adjust your filters.") # Display an informational message if no restaurants are found.

# --- Footer ---
st.markdown(
    """
    <hr style="margin-top: 50px; border-top: 1px solid #eee;">
    <p style="text-align: center; color: #999; font-size: 0.8em;">
        Built with ❤️ using Streamlit. Data is for demonstration purposes only.
    </p>
    """,
    unsafe_allow_html=True
)
