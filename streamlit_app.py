import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
import base64
import io
import numpy as np # Import numpy for NaN values

# --- CSV File Configuration ---
RESTAURANTS_CSV_FILE = "restaurants.csv"
REVIEWS_CSV_FILE = "reviews.csv"

# --- Utility Function to ensure DataFrame schema is correct ---
def validate_and_update_dataframe(df):
    """
    Checks for the presence of 'Private Room' and 'Max Capacity' columns
    and adds them with default values if they are missing.
    """
    if 'Private Room' not in df.columns:
        df['Private Room'] = 'No'
    if 'Max Capacity' not in df.columns:
        df['Max Capacity'] = np.nan
    # Ensure 'Max Capacity' is of numeric type for filtering
    df['Max Capacity'] = pd.to_numeric(df['Max Capacity'], errors='coerce')
    return df

# --- Initialize CSV files and ensure they have the correct schema ---
def initialize_csv_files():
    """
    Initializes the restaurants.csv and reviews.csv files with headers.
    If the files exist, it checks and adds new columns to avoid KeyErrors.
    """
    # Restaurant data initialization
    if not os.path.exists(RESTAURANTS_CSV_FILE):
        restaurant_data = [
            {
                "Name": "The Dempsey Cookhouse & Bar",
                "Cuisine": "Modern European",
                "Location": "Dempsey Hill",
                "Rating": 4.5,
                "Price Range": "$$$",
                "Description": "Chic restaurant by Jean-Georges Vongerichten, offering a sophisticated dining experience.",
                "Image": "https://placehold.co/600x400/FF5733/FFFFFF?text=Dempsey+Cookhouse",
                "Address": "17D Dempsey Rd, Singapore 249676",
                "Private Room": "No",
                "Max Capacity": None
            },
            {
                "Name": "Odette",
                "Cuisine": "French",
                "Location": "City Hall",
                "Rating": 5.0,
                "Price Range": "$$$$",
                "Description": "Three Michelin-starred modern French restaurant, known for its exquisite tasting menus.",
                "Image": "https://placehold.co/600x400/33FF57/000000?text=Odette",
                "Address": "1 St Andrew's Rd, #01-04 National Gallery, Singapore 178957",
                "Private Room": "Yes",
                "Max Capacity": 12
            },
            {
                "Name": "Burnt Ends",
                "Cuisine": "Australian BBQ",
                "Location": "Outram Park",
                "Rating": 4.7,
                "Price Range": "$$$",
                "Description": "Modern Australian barbecue with an open-concept kitchen and custom-built ovens.",
                "Image": "https://placehold.co/600x400/3357FF/FFFFFF?text=Burnt+Ends",
                "Address": "7 Dempsey Rd, #01-04, Singapore 249671",
                "Private Room": "No",
                "Max Capacity": None
            },
            {
                "Name": "Candlenut",
                "Cuisine": "Peranakan",
                "Location": "Dempsey Hill",
                "Rating": 4.3,
                "Price Range": "$$",
                "Description": "The world's first Michelin-starred Peranakan restaurant, offering refined Straits-Chinese cuisine.",
                "Image": "https://placehold.co/600x400/FF33A1/FFFFFF?text=Candlenut",
                "Address": "17A Dempsey Rd, Singapore 249676",
                "Private Room": "Yes",
                "Max Capacity": 8
            },
            {
                "Name": "Jumbo Seafood",
                "Cuisine": "Seafood",
                "Location": "Riverside Point",
                "Rating": 4.2,
                "Price Range": "$$",
                "Description": "Famous for its Chili Crab and Black Pepper Crab, a must-visit for seafood lovers.",
                "Image": "https://placehold.co/600x400/A1FF33/000000?text=Jumbo+Seafood",
                "Address": "301 Upper East Coast Rd, Singapore 466444",
                "Private Room": "Yes",
                "Max Capacity": 20
            },
            {
                "Name": "Tiong Bahru Bakery",
                "Cuisine": "Cafe",
                "Location": "Tiong Bahru",
                "Rating": 4.0,
                "Price Range": "$",
                "Description": "Popular spot for freshly baked pastries, coffee, and a relaxed atmosphere.",
                "Image": "https://placehold.co/600x400/33A1FF/FFFFFF?text=Tiong+Bahru+Bakery",
                "Address": "56 Eng Hoon St, #01-70, Singapore 160056",
                "Private Room": "No",
                "Max Capacity": None
            },
            {
                "Name": "Newton Food Centre",
                "Cuisine": "Local Hawker",
                "Location": "Newton",
                "Rating": 3.8,
                "Price Range": "$",
                "Description": "An iconic hawker centre offering a wide variety of local Singaporean dishes.",
                "Image": "https://placehold.co/600x400/FFBB33/000000?text=Newton+Food+Centre",
                "Address": "500 Clemenceau Ave N, Singapore 229495",
                "Private Room": "No",
                "Max Capacity": None
            },
            {
                "Name": "PS.Cafe Harding Road",
                "Cuisine": "Western/Cafe",
                "Location": "Dempsey Hill",
                "Rating": 4.1,
                "Price Range": "$$",
                "Description": "A popular cafe chain known for its truffle fries, relaxed ambiance, and lush surroundings.",
                "Image": "https://placehold.co/600x400/BB33FF/FFFFFF?text=PS.Cafe",
                "Address": "28B Harding Rd, Singapore 249549",
                "Private Room": "Yes",
                "Max Capacity": 6
            },
            {
                "Name": "National Kitchen by Violet Oon",
                "Cuisine": "Peranakan",
                "Location": "City Hall",
                "Rating": 4.4,
                "Price Range": "$$$",
                "Description": "Elegant restaurant serving classic Peranakan dishes in a grand setting at the National Gallery.",
                "Image": "https://placehold.co/600x400/33FFBB/000000?text=National+Kitchen",
                "Address": "1 St Andrew's Rd, #02-01 National Gallery, Singapore 178957",
                "Private Room": "Yes",
                "Max Capacity": 10
            },
            {
                "Name": "Les Amis",
                "Cuisine": "French",
                "Location": "Orchard",
                "Rating": 4.9,
                "Price Range": "$$$$",
                "Description": "One of Singapore's oldest independent fine-dining French restaurants, with three Michelin stars.",
                "Image": "https://placehold.co/600x400/FF3333/FFFFFF?text=Les+Amis",
                "Address": "1 Scotts Rd, #02-16 Shaw Centre, Singapore 228208",
                "Private Room": "Yes",
                "Max Capacity": 16
            }
        ]
        initial_restaurants_df = pd.DataFrame(restaurant_data)
        initial_restaurants_df.to_csv(RESTAURANTS_CSV_FILE, index=False)
        with st.empty():
            st.success("Restaurants data initialized.", icon="✅")
            time.sleep(2)
    
    # Reviews data initialization
    if not os.path.exists(REVIEWS_CSV_FILE):
        initial_reviews_df = pd.DataFrame(columns=[
            "restaurant_name", "rating", "review_text",
            "reviewer_name", "reviewer_department", "reviewer_designation",
            "timestamp"
        ])
        initial_reviews_df.to_csv(REVIEWS_CSV_FILE, index=False)

initialize_csv_files()

# --- Session State Initialization ---
if 'review_restaurant_name' not in st.session_state:
    st.session_state.review_restaurant_name = None
if 'review_submitted_message' not in st.session_state:
    st.session_state.review_submitted_message = None
if 'show_add_restaurant_form' not in st.session_state:
    st.session_state.show_add_restaurant_form = False
if 'add_restaurant_submitted' not in st.session_state:
    st.session_state.add_restaurant_submitted = False
if 'new_location_selected' not in st.session_state:
    st.session_state.new_location_selected = False
if 'df' not in st.session_state:
    st.session_state.df = None

# --- Load restaurant data from CSV ---
@st.cache_data
def load_restaurants(file_path=RESTAURANTS_CSV_FILE):
    """Loads all restaurant data from a specified CSV file path."""
    try:
        df_restaurants = pd.read_csv(file_path)
        # Ensure the DataFrame has the correct columns, regardless of the source
        df_restaurants = validate_and_update_dataframe(df_restaurants)
        return df_restaurants
    except FileNotFoundError:
        st.error(f"Restaurant data file not found at {file_path}. Please re-run the app or upload a new file.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="Singapore Restaurant Guide",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        font-size: 3em;
        color: #2F4F4F;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
    }

    .subheader {
        font-size: 1.5em;
        color: #4682B4;
        margin-top: 20px;
        margin-bottom: 15px;
        font-weight: 600;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }
    
    .stTextArea > label {
      color: #666;
    }
    .stTextArea > div > div {
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }

    .stSelectbox > div > div {
        border-radius: 10px;
        border: 1px solid #ccc;
    }

    .stButton > button {
        background-color: #17a589;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s ease, color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #48c9b0;
        color: #333;
    }

    .restaurant-card {
        background-color: #f9f9f9;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .restaurant-card img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .restaurant-name {
        font-size: 1.8em;
        color: #2F4F4F;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .restaurant-details {
        font-size: 1.1em;
        color: #555;
        margin-bottom: 8px;
    }

    .restaurant-description {
        font-size: 0.95em;
        color: #666;
        line-height: 1.5;
        flex-grow: 1;
    }
    
    .st-emotion-cache-1cypcdb {
        padding-top: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Function to Save Review to CSV ---
def save_review_to_csv(restaurant_name, rating, review_text, reviewer_name, reviewer_department, reviewer_designation):
    """Saves a review to the CSV file."""
    try:
        reviews_df = pd.read_csv(REVIEWS_CSV_FILE)
        new_review = pd.DataFrame([{
            "restaurant_name": restaurant_name,
            "rating": rating,
            "review_text": review_text,
            "reviewer_name": reviewer_name,
            "reviewer_department": reviewer_department,
            "reviewer_designation": reviewer_designation,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        reviews_df = pd.concat([reviews_df, new_review], ignore_index=True)
        reviews_df.to_csv(REVIEWS_CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving review to CSV: {e}")
        return False

# --- Function to Add a New Restaurant to CSV ---
def add_restaurant_to_csv(name, cuisine, location, rating, price_range, description, image, address, private_room, max_capacity):
    """Adds a new restaurant to the restaurants.csv file."""
    try:
        restaurants_df = pd.read_csv(RESTAURANTS_CSV_FILE)
        if name in restaurants_df['Name'].values:
            st.warning("A restaurant with this name already exists. Please use a unique name.")
            return False

        new_restaurant = pd.DataFrame([{
            "Name": name,
            "Cuisine": cuisine,
            "Location": location,
            "Rating": rating,
            "Price Range": price_range,
            "Description": description,
            "Image": image,
            "Address": address,
            "Private Room": private_room,
            "Max Capacity": max_capacity
        }])
        
        restaurants_df = pd.concat([restaurants_df, new_restaurant], ignore_index=True)
        restaurants_df.to_csv(RESTAURANTS_CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving new restaurant to CSV: {e}")
        return False

# --- Function to Load Reviews from CSV ---
def load_reviews_from_csv(restaurant_name=None):
    """Loads reviews from the CSV file, optionally filtering for a specific restaurant."""
    try:
        reviews_df = pd.read_csv(REVIEWS_CSV_FILE)
        if restaurant_name:
            restaurant_reviews = reviews_df[reviews_df["restaurant_name"] == restaurant_name]
            restaurant_reviews = restaurant_reviews.sort_values(by="timestamp", ascending=False)
            return restaurant_reviews.to_dict(orient="records")
        return reviews_df
    except FileNotFoundError:
        return pd.DataFrame() if not restaurant_name else []
    except Exception as e:
        st.error(f"Error loading reviews from CSV: {e}")
        return pd.DataFrame() if not restaurant_name else []

# --- App Title and Header ---
st.markdown('<h1 class="main-header">🍽️ Singapore Restaurant Guide</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1em;">Discover and add the best dining experiences in Singapore!</p>', unsafe_allow_html=True)

# --- Sidebar for File Upload and Filters ---
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload your own restaurant database (CSV)", type=["csv"], help="Upload a CSV file with 'Name', 'Cuisine', 'Location', 'Rating', 'Price Range', 'Description', 'Image', 'Address', 'Private Room', and 'Max Capacity' columns.")

if uploaded_file is not None:
    # Load and validate the uploaded file
    df_uploaded = pd.read_csv(uploaded_file)
    st.session_state.df = validate_and_update_dataframe(df_uploaded)
    st.cache_data.clear()
else:
    if st.session_state.df is None:
        st.session_state.df = load_restaurants()
    elif 'uploaded_file' in st.session_state and st.session_state.uploaded_file is None:
        st.session_state.df = load_restaurants()
        st.cache_data.clear()

df = st.session_state.df

if not df.empty:
    csv_restaurants = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download Restaurants",
        data=csv_restaurants,
        file_name='restaurants_database.csv',
        mime='text/csv',
        help="Click here to download the current list of restaurants as a CSV file."
    )

reviews_df = load_reviews_from_csv()
if not reviews_df.empty:
    csv_reviews = reviews_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download All Reviews",
        data=csv_reviews,
        file_name='restaurant_reviews.csv',
        mime='text/csv',
        help="Click here to download all submitted reviews as a CSV file."
    )
st.sidebar.markdown("---")

st.sidebar.header("Filter Restaurants")

search_query = st.sidebar.text_input("Search by Name or Description", "")

if not df.empty:
    cuisine_options = ["All"] + sorted(df["Cuisine"].unique().tolist())
    selected_cuisine = st.sidebar.selectbox("Select Cuisine", cuisine_options)

    location_options = ["All"] + sorted(df["Location"].unique().tolist())
    selected_location_filter = st.sidebar.selectbox("Select Location", location_options)

    price_range_options = ["All", "$", "$$", "$$$", "$$$$"]
    selected_price_range = st.sidebar.selectbox("Select Price Range", price_range_options)

    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.1)
    
    # Using a hardcoded list to avoid KeyError on a fresh or user-uploaded CSV
    private_room_options = ["All", "Yes", "No"]
    selected_private_room_filter = st.sidebar.selectbox("Private Room Available?", private_room_options)

    min_capacity_filter = None
    if selected_private_room_filter == "Yes":
        # Get valid capacities from the DataFrame to set a realistic max value for the slider
        valid_capacities = df[df['Private Room'] == 'Yes']['Max Capacity'].dropna().tolist()
        if valid_capacities:
            max_possible_capacity = int(max(valid_capacities))
            min_capacity_filter = st.sidebar.slider("Minimum Private Room Capacity", 1, max_possible_capacity, 1)
        else:
            st.sidebar.info("No restaurants with private rooms have a capacity specified.")


    # --- Apply Filters ---
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df["Name"].str.contains(search_query, case=False, na=False) |
            filtered_df["Description"].str.contains(search_query, case=False, na=False)
        ]

    if selected_cuisine != "All":
        filtered_df = filtered_df[filtered_df["Cuisine"] == selected_cuisine]

    if selected_location_filter != "All":
        filtered_df = filtered_df[filtered_df["Location"] == selected_location_filter]

    if selected_price_range != "All":
        filtered_df = filtered_df[filtered_df["Price Range"] == selected_price_range]

    filtered_df = filtered_df[filtered_df["Rating"] >= min_rating]
    
    if selected_private_room_filter != "All":
        filtered_df = filtered_df[filtered_df["Private Room"] == selected_private_room_filter]
        if selected_private_room_filter == "Yes" and min_capacity_filter is not None:
            # Check for NaN values before filtering
            filtered_df = filtered_df[pd.to_numeric(filtered_df['Max Capacity'], errors='coerce').notna()]
            filtered_df = filtered_df[filtered_df["Max Capacity"] >= min_capacity_filter]

else:
    filtered_df = pd.DataFrame()


# --- Add New Restaurant Button ---
st.write("Have a new restaurant to include? ")
if st.button("➕ Add a New Restaurant"):
    st.session_state.show_add_restaurant_form = True
    st.session_state.new_location_selected = False

# --- Add New Restaurant Form (simulated pop-up) ---
if st.session_state.show_add_restaurant_form:
    with st.container(border=True):
        st.markdown('<h3 style="text-align: center;">Enter New Restaurant Details</h3>', unsafe_allow_html=True)

        new_name = st.text_input("Restaurant Name", help="The name of the restaurant.")
        new_cuisine = st.text_input("Cuisine", help="e.g., Italian, Japanese, Local Hawker.")
        
        existing_locations = sorted(df["Location"].unique().tolist()) if not df.empty else []
        locations = existing_locations + ["Add new location..."]
        
        def handle_location_change():
            if st.session_state.location_selectbox == "Add new location...":
                st.session_state.new_location_selected = True
            else:
                st.session_state.new_location_selected = False

        selected_location = st.selectbox(
            "Location", 
            options=locations, 
            index=0 if locations else None,
            key="location_selectbox",
            on_change=handle_location_change,
            help="Select a pre-existing location or add a new one."
        )
        
        if st.session_state.new_location_selected:
            final_location = st.text_input("Enter New Location", key="new_location_text_input", help="Type in a new location.")
        else:
            final_location = selected_location
        
        new_address = st.text_input("Address", help="The full address of the restaurant.")
        new_rating = st.slider("Rating", 0.0, 5.0, 3.0, 0.1, help="Overall rating of the restaurant.")
        new_price = st.selectbox("Price Range", ["$", "$$", "$$$", "$$$$"], index=1, help="$, $$, $$$, or $$$$.")
        new_description = st.text_area("Description", help="A brief description of the restaurant.")
        uploaded_image = st.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg"], help="Upload a photo of the restaurant.")

        new_private_room = st.selectbox("Private Room Available?", ["No", "Yes"], help="Does the restaurant have a private room?")
        new_capacity = None
        if new_private_room == "Yes":
            new_capacity = st.number_input("Max Capacity of Private Room", min_value=1, value=10, step=1, help="Maximum number of people the private room can hold.")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Add", key="add_restaurant_button"):
                if new_name and new_cuisine and final_location and new_description and new_address:
                    image_data = ""
                    if uploaded_image is not None:
                        bytes_data = uploaded_image.getvalue()
                        b64_encoded_image = base64.b64encode(bytes_data).decode('utf-8')
                        image_data = f"data:{uploaded_image.type};base64,{b64_encoded_image}"
                    else:
                        image_data = "https://placehold.co/600x400/CCCCCC/000000?text=Image+Not+Available"
                    
                    if add_restaurant_to_csv(new_name, new_cuisine, final_location, new_rating, new_price, new_description, image_data, new_address, new_private_room, new_capacity):
                        st.session_state.add_restaurant_submitted = True
                        st.session_state.show_add_restaurant_form = False
                        st.success(f"Restaurant '{new_name}' added successfully!", icon="✅")
                        st.cache_data.clear()
                        time.sleep(2)
                        st.rerun()
                else:
                    st.error("Please fill in all required fields (Name, Cuisine, Location, Address, Description).", icon="⚠️")

        with col3:
            _, button_col = st.columns([1, 0.5])
            with button_col:
                if st.button("Close", key="close_add_restaurant_form"):
                    st.session_state.show_add_restaurant_form = False
                    st.rerun()

# --- Display Results ---
st.markdown('<h2 class="subheader">Available Restaurants</h2>', unsafe_allow_html=True)

if not filtered_df.empty:
    cols = st.columns(3)
    col_index = 0

    for index, row in filtered_df.iterrows():
        with cols[col_index]:
            with st.container(border=True):
                image_src = row.get('Image')
                image_tag = ""
                if isinstance(image_src, str):
                    if image_src.startswith("http"):
                        image_tag = f'<img src="{image_src}" alt="{row["Name"]}" onerror="this.onerror=null;this.src=\'https://placehold.co/600x400/CCCCCC/000000?text=Image+Not+Found\';" style="width: 100%; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 15px;">'
                    else:
                        image_tag = f'<img src="{image_src}" alt="{row["Name"]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 15px;">'
                else:
                    image_tag = f'<img src="https://placehold.co/600x400/CCCCCC/000000?text=Image+Not+Available" alt="{row["Name"]}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 15px;">'

                private_room_info = f"<strong>Private Room:</strong> {row.get('Private Room', 'N/A')}"
                if row.get('Private Room', 'N/A') == "Yes" and pd.notna(row.get('Max Capacity')):
                    private_room_info += f" (Max Capacity: {int(row['Max Capacity'])})"

                st.markdown(f"""
                <div class="restaurant-card">
                    {image_tag}
                    <div class="restaurant-name">{row['Name']}</div>
                    <div class="restaurant-details">
                        <strong>Cuisine:</strong> {row['Cuisine']}<br>
                        <strong>Location:</strong> {row['Location']}<br>
                        <strong>Address:</strong> {row['Address']}<br>
                        <strong>Rating:</strong> {row['Rating']} ⭐<br>
                        <strong>Price:</strong> {row['Price Range']}<br>
                        {private_room_info}
                    </div>
                    <div class="restaurant-description">{row['Description']}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Submit Review", key=f"submit_review_for_{row['Name']}"):
                    st.session_state.review_restaurant_name = row['Name']
                    st.session_state.review_submitted_message = None
                    st.rerun()

                if st.session_state.review_restaurant_name == row['Name']:
                    st.markdown(f"**Review for {row['Name']}:**")
                    reviewer_name = st.text_input("Your Name:", key=f"reviewer_name_{row['Name']}")
                    reviewer_department = st.text_input("Your Department:", key=f"reviewer_dept_{row['Name']}")
                    reviewer_designation = st.text_input("Your Designation:", key=f"reviewer_designation_{row['Name']}")
                    review_rating = st.slider("Rating", 0.0, 5.0, 3.0, 0.5, key=f"review_rating_{row['Name']}")
                    review_text = st.text_area("Your comments:", key=f"review_text_{row['Name']}")
                    
                    submit_col, cancel_col = st.columns(2)
                    with submit_col:
                        if st.button("Submit", key=f"submit_review_form_{row['Name']}"):
                            if review_text and reviewer_name:
                                if save_review_to_csv(row['Name'], review_rating, review_text, reviewer_name, reviewer_department, reviewer_designation):
                                    st.session_state.review_submitted_message = f"Thank you for your review of {row['Name']}! Rating: {review_rating} ⭐"
                                    st.session_state.review_restaurant_name = None
                                    st.rerun()
                            else:
                                st.warning("Please provide your name and review comments before submitting.", icon="⚠️")
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_review_form_{row['Name']}"):
                            st.session_state.review_restaurant_name = None
                            st.session_state.review_submitted_message = None
                            st.rerun()

                if st.session_state.review_submitted_message and st.session_state.review_restaurant_name is None:
                    if st.session_state.review_submitted_message.startswith(f"Thank you for your review of {row['Name']}"):
                        st.success(st.session_state.review_submitted_message, icon="✅")
                        st.session_state.review_submitted_message = None
                
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
                            st.markdown("---")
                    else:
                        st.info("No reviews yet for this restaurant.")

        col_index = (col_index + 1) % 3
else:
    st.info("No restaurants found matching your criteria. Please adjust your filters.")

# --- Footer ---
st.markdown(
    """
    <hr style="margin-top: 50px; border-top: 1px solid #eee;">
    <p style="text-align: center; color: #999; font-size: 0.8em;">
        Built with ❤️ using Streamlit.
    </p>
    """,
    unsafe_allow_html=True
)
