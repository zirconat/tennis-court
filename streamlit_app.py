import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
import base64
import io
import numpy as np
import re

# --- CSV File Configuration ---
# Define the file paths for all data storage.
RESTAURANTS_CSV_FILE = "restaurants.csv"
REVIEWS_CSV_FILE = "reviews.csv"
MENUS_CSV_FILE = "menus.csv"
GALLERY_CSV_FILE = "gallery_images.csv"

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
    Initializes the restaurants.csv, reviews.csv, menus.csv, and gallery_images.csv files with headers.
    If the files exist, it checks and adds new columns to avoid KeyErrors.
    """
    # Restaurant data initialization
    if not os.path.exists(RESTAURANTS_CSV_FILE):
        empty_df = pd.DataFrame(columns=[
            "Name", "Cuisine", "Location", "Rating", "Price Range",
            "Description", "Image", "Address", "Private Room", "Max Capacity"
        ])
        empty_df.to_csv(RESTAURANTS_CSV_FILE, index=False)
        with st.empty():
            st.success("Restaurants data file created.", icon="✅")
            time.sleep(2)

    # Reviews data initialization
    if not os.path.exists(REVIEWS_CSV_FILE):
        initial_reviews_df = pd.DataFrame(columns=[
            "restaurant_name", "rating", "review_text",
            "reviewer_name", "reviewer_department", "reviewer_designation",
            "timestamp"
        ])
        initial_reviews_df.to_csv(REVIEWS_CSV_FILE, index=False)
        
    # Menus data initialization with new columns for file uploads
    if not os.path.exists(MENUS_CSV_FILE):
        initial_menus_df = pd.DataFrame(columns=[
            "restaurant_name", "file_name", "file_type", "base64_data", "timestamp"
        ])
        initial_menus_df.to_csv(MENUS_CSV_FILE, index=False)
        
    # Gallery data initialization
    if not os.path.exists(GALLERY_CSV_FILE):
        initial_gallery_df = pd.DataFrame(columns=[
            "restaurant_name", "file_name", "file_type", "base64_data", "timestamp"
        ])
        initial_gallery_df.to_csv(GALLERY_CSV_FILE, index=False)

# Call the function to ensure all necessary CSVs exist before running the app
initialize_csv_files()

# --- Session State Initialization ---
# Initialize session state variables to manage UI and data flow
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
if 'add_menu_for_restaurant' not in st.session_state:
    st.session_state.add_menu_for_restaurant = None
if 'add_photo_for_restaurant' not in st.session_state:
    st.session_state.add_photo_for_restaurant = None
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

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
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3em;
        color: #2F4F4F;
        text-align: center;
        margin-bottom: 30px;
        font-weight: 700;
    }

    .subheader {
        font-family: 'Inter', sans-serif;
        font-size: 1.5em;
        color: #4682B4;
        margin-top: 20px;
        margin-bottom: 15px;
        font-weight: 600;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        font-family: 'Inter', sans-serif;
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }
    
    .stTextArea > label {
      color: #666;
    }
    .stTextArea > div > div {
        font-family: 'Inter', sans-serif;
        border-radius: 10px;
        border: 1px solid #ccc;
        padding: 8px 12px;
    }

    .stSelectbox > div > div {
        font-family: 'Inter', sans-serif;
        border-radius: 10px;
        border: 1px solid #ccc;
    }

    .stButton > button {
        font-family: 'Inter', sans-serif;
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
    
    .st-emotion-cache-1cypcdb {
        padding-top: 0rem;
    }

    .restaurant-card {
        font-family: 'Inter', sans-serif;
        background-color: #f9f9f9;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .restaurant-name {
        font-family: 'Inter', sans-serif;
        font-size: 1.8em;
        color: #2F4F4F;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .restaurant-details {
        font-family: 'Inter', sans-serif;
        font-size: 1.1em;
        color: #555;
        margin-bottom: 8px;
    }

    .restaurant-description {
        font-family: 'Inter', sans-serif;
        font-size: 0.95em;
        color: #666;
        line-height: 1.5;
        flex-grow: 1;
    }
    
    .st-emotion-cache-1p6f5x6 > div {
        padding-top: 0px;
    }

    /* Additional styling for the gallery controls */
    .gallery-controls-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 10px;
    }
    .gallery-counter {
        margin: 0 10px;
        font-size: 1em;
        color: #555;
    }

    .sidebar-message {
        font-size: 0.9em;
        color: #555;
        text-align: center;
        margin-bottom: 1rem;
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
        
# --- Function to Load Menus from CSV ---
def load_menus_from_csv(restaurant_name=None):
    """Loads menus from the CSV file, optionally filtering for a specific restaurant."""
    try:
        menus_df = pd.read_csv(MENUS_CSV_FILE)
        if restaurant_name:
            restaurant_menus = menus_df[menus_df["restaurant_name"] == restaurant_name]
            return restaurant_menus.to_dict(orient="records")
        return menus_df
    except FileNotFoundError:
        return pd.DataFrame() if not restaurant_name else []
    except Exception as e:
        st.error(f"Error loading menus from CSV: {e}")
        return pd.DataFrame() if not restaurant_name else []
        
# --- Function to Add a New Menu Item (File) to CSV ---
def add_menu_item_to_csv(restaurant_name, file_name, file_type, base64_data):
    """Adds a new menu item file to the menus.csv file."""
    try:
        menus_df = pd.read_csv(MENUS_CSV_FILE)
        new_menu = pd.DataFrame([{
            "restaurant_name": restaurant_name,
            "file_name": file_name,
            "file_type": file_type,
            "base64_data": base64_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        menus_df = pd.concat([menus_df, new_menu], ignore_index=True)
        menus_df.to_csv(MENUS_CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving new menu item file to CSV: {e}")
        return False
        
# --- Function to Add a New Gallery Image to CSV ---
def add_gallery_image_to_csv(restaurant_name, file_name, file_type, base64_data):
    """Adds a new gallery image to the gallery_images.csv file."""
    try:
        gallery_df = pd.read_csv(GALLERY_CSV_FILE)
        new_image = pd.DataFrame([{
            "restaurant_name": restaurant_name,
            "file_name": file_name,
            "file_type": file_type,
            "base64_data": base64_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        gallery_df = pd.concat([gallery_df, new_image], ignore_index=True)
        gallery_df.to_csv(GALLERY_CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving new gallery image to CSV: {e}")
        return False

# --- Function to Load Gallery Images from CSV ---
def load_gallery_images_from_csv(restaurant_name=None):
    """Loads gallery images from the CSV file, optionally filtering for a specific restaurant."""
    try:
        gallery_df = pd.read_csv(GALLERY_CSV_FILE)
        if restaurant_name:
            restaurant_images = gallery_df[gallery_df["restaurant_name"] == restaurant_name]
            return restaurant_images.to_dict(orient="records")
        return gallery_df
    except FileNotFoundError:
        return pd.DataFrame() if not restaurant_name else []
    except Exception as e:
        st.error(f"Error loading gallery images from CSV: {e}")
        return pd.DataFrame() if not restaurant_name else []
        
# --- Function to find restaurants based on filters ---
def find_restaurants(df_restaurants, df_reviews, search_query, selected_cuisine, selected_location_filter, selected_price_range, min_rating, selected_private_room_filter, min_capacity_filter):
    """
    Finds restaurants based on the provided filters and an improved search query,
    now including support for exact phrases (""), AND (&), and OR (,) conditions.
    """
    filtered_df = df_restaurants.copy()
    
    # 1. Handle Search Query
    if search_query:
        # Step 1: Initialize an empty DataFrame to store all matching restaurants
        combined_matches = pd.DataFrame(columns=filtered_df.columns)
        
        # Step 2: Split query into individual terms based on commas (OR) or ampersands (AND)
        if '&' in search_query:
            search_terms = [term.strip() for term in search_query.split('&')]
            operator = 'AND'
        else:
            search_terms = [term.strip() for term in search_query.split(',')]
            operator = 'OR'

        first_term = True
        for term in search_terms:
            current_matches = pd.DataFrame(columns=filtered_df.columns)
            
            # Check for exact phrase search
            if term.startswith('"') and term.endswith('"'):
                exact_phrase = term.strip('"')
                
                # Regex search for the exact phrase in Name, Description, and reviews
                name_desc_matches = filtered_df[
                    filtered_df["Name"].str.contains(re.escape(exact_phrase), case=False, na=False) |
                    filtered_df["Description"].str.contains(re.escape(exact_phrase), case=False, na=False)
                ]
                
                # Find matching restaurants based on review text
                matching_review_names = df_reviews[
                    df_reviews['review_text'].str.contains(re.escape(exact_phrase), case=False, na=False)
                ]['restaurant_name'].unique()
                review_matches = filtered_df[filtered_df['Name'].isin(matching_review_names)]
                
                current_matches = pd.concat([name_desc_matches, review_matches]).drop_duplicates(subset=["Name"])
                
            else:
                # Regular substring search for the term
                name_desc_matches = filtered_df[
                    filtered_df["Name"].str.contains(term, case=False, na=False) |
                    filtered_df["Description"].str.contains(term, case=False, na=False)
                ]
                
                # Find matching restaurants based on review text
                matching_review_names = df_reviews[
                    df_reviews['review_text'].str.contains(term, case=False, na=False)
                ]['restaurant_name'].unique()
                review_matches = filtered_df[filtered_df['Name'].isin(matching_review_names)]
                
                current_matches = pd.concat([name_desc_matches, review_matches]).drop_duplicates(subset=["Name"])
            
            if operator == 'OR':
                combined_matches = pd.concat([combined_matches, current_matches]).drop_duplicates(subset=["Name"])
            elif operator == 'AND':
                if first_term:
                    combined_matches = current_matches
                    first_term = False
                else:
                    # Keep only restaurants that are in both the previous and current matches
                    combined_matches = combined_matches.merge(current_matches, on=filtered_df.columns.tolist())
        
        # Apply the search results for subsequent filtering
        filtered_df = combined_matches.reset_index(drop=True)
    
    # 2. Apply Other Filters
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
    
    return filtered_df


# --- App Title and Header ---
st.markdown('<h1 class="main-header">🍽️ Singapore Restaurant Guide</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 1.1em; font-family: \'Inter\', sans-serif;">Discover and add the best dining experiences in Singapore!</p>', unsafe_allow_html=True)
    
# --- Sidebar for File Upload and Filters (Admin-only section) ---

st.sidebar.caption("For admin use only")
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
            
    menus_df = load_menus_from_csv()
    if not menus_df.empty:
        csv_menus = menus_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download All Menus",
            data=csv_menus,
            file_name='restaurant_menus.csv',
            mime='text/csv',
            help="Click here to download all submitted menus as a CSV file."
        )
            
    gallery_df = load_gallery_images_from_csv()
    if not gallery_df.empty:
        csv_gallery = gallery_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download All Gallery Images",
            data=csv_gallery,
            file_name='restaurant_gallery.csv',
            mime='text/csv',
            help="Click here to download all submitted gallery images as a CSV file."
        )

    st.sidebar.markdown("---")

    st.sidebar.header("Filter Restaurants")

    search_query = st.sidebar.text_input("Search by Restaurant Name, Description, or Reviews", "")

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
        reviews_df = reviews_df.copy()

        filtered_df = find_restaurants(
            df_restaurants=df,
            df_reviews=reviews_df,
            search_query=search_query,
            selected_cuisine=selected_cuisine,
            selected_location_filter=selected_location_filter,
            selected_price_range=selected_price_range,
            min_rating=min_rating,
            selected_private_room_filter=selected_private_room_filter,
            min_capacity_filter=min_capacity_filter
        )
        
    else:
        filtered_df = pd.DataFrame()
        
    
    
# --- Add New Restaurant Button (Regular user) ---
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
        
        new_private_room = st.selectbox("Private Room Available?", ["No", "Yes"], help="Does the restaurant have a private room?")
        new_capacity = None
        if new_private_room == "Yes":
            new_capacity = st.number_input("Max Capacity of Private Room", min_value=1, value=10, step=1, help="Maximum number of people the private room can hold.")
                
        new_image_file = st.file_uploader(
            "Upload an Image",
            type=["png", "jpg", "jpeg"],
            help="Upload a photo of the restaurant (optional)."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Add", key="add_restaurant_button"):
                if new_name and new_cuisine and final_location and new_description and new_address:
                    image_data = None
                    if new_image_file is not None:
                        # Read file as bytes and encode to base64
                        file_bytes = new_image_file.getvalue()
                        base64_data = base64.b64encode(file_bytes).decode('utf-8')
                        image_data = f"data:{new_image_file.type};base64,{base64_data}"
                    else:
                        # Use a default placeholder if no image is uploaded
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
                restaurant_name = row['Name']

                # Load gallery images for the current restaurant
                gallery_images = load_gallery_images_from_csv(restaurant_name)
                
                # Check if a gallery index exists for this restaurant, if not, initialize it to 0
                if f'gallery_index_{restaurant_name}' not in st.session_state:
                    st.session_state[f'gallery_index_{restaurant_name}'] = 0

                # Display the photo gallery
                with st.container():
                    # The gallery buttons and image are placed in a container for a cohesive look
                    st.markdown('<div class="fixed-gallery-container">', unsafe_allow_html=True)
                    if gallery_images:
                        current_image_index = st.session_state[f'gallery_index_{restaurant_name}']
                        current_image_data = gallery_images[current_image_index]
                            
                        # Use columns to place the buttons on the sides of the image
                        btn_col_prev, img_col, btn_col_next = st.columns([1, 6, 1])

                        with btn_col_prev:
                            # Button to go to the previous image, disabled at the first image
                            if st.button("◀", key=f"prev_{restaurant_name}", disabled=(current_image_index == 0), help="Previous photo"):
                                st.session_state[f'gallery_index_{restaurant_name}'] -= 1
                                st.rerun()
                                    
                        with img_col:
                            # Display the current image in the central column
                            st.image(
                                f"data:{current_image_data['file_type']};base64,{current_image_data['base64_data']}", 
                                use_container_width=True
                            )
                            
                        with btn_col_next:
                            # Button to go to the next image, disabled at the last image
                            if st.button("▶", key=f"next_{restaurant_name}", disabled=(current_image_index == len(gallery_images) - 1), help="Next photo"):
                                st.session_state[f'gallery_index_{restaurant_name}'] += 1
                                st.rerun()
                            
                        st.markdown(f'<p style="text-align:center; margin-top: 10px;">{current_image_index + 1} of {len(gallery_images)}</p>', unsafe_allow_html=True)

                    else:
                        # If no images, show a placeholder inside the fixed container
                        st.image("https://placehold.co/1600x900/CCCCCC/000000?text=Image+Not+Available", use_container_width=True)

                private_room_info = f"<strong>Private Room:</strong> {row.get('Private Room', 'N/A')}"
                if row.get('Private Room', 'N/A') == "Yes" and pd.notna(row.get('Max Capacity')):
                    private_room_info += f" (Max Capacity: {int(row['Max Capacity'])})"

                st.markdown(f"""
                <div class="restaurant-card">
                    <div class="restaurant-name">{row['Name']}</div>
                    <div class="restaurant-details">
                        <strong>Cuisine:</strong> {row['Cuisine']}<br>
                        <strong>Location:</strong> {row['Location']}<br>
                        <strong>Address:</strong> {row['Address']}<br>
                        <strong>Rating:</strong> {row['Rating']:.1f} ⭐<br>
                        <strong>Price:</strong> {row['Price Range']}<br>
                        {private_room_info}
                    </div>
                    <div class="restaurant-description">{row['Description']}</div>
                </div>
                """, unsafe_allow_html=True)
                    
                # Create a four-column layout for the buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)

                with btn_col1:
                    if st.button("Submit Review", key=f"submit_review_for_{row['Name']}"):
                        st.session_state.review_restaurant_name = row['Name']
                        st.session_state.review_submitted_message = None
                        st.session_state.add_menu_for_restaurant = None # Close menu form
                        st.session_state.add_photo_for_restaurant = None # Close photo upload form
                        st.rerun()
                    
                with btn_col2:
                    if st.button("Upload Menu", key=f"add_menu_for_{row['Name']}"):
                        st.session_state.add_menu_for_restaurant = row['Name']
                        st.session_state.review_restaurant_name = None # Close review form
                        st.session_state.add_photo_for_restaurant = None # Close photo upload form
                        st.rerun()

                with btn_col3:
                    if st.button("Upload Photo", key=f"add_photo_for_{row['Name']}"):
                        st.session_state.add_photo_for_restaurant = row['Name']
                        st.session_state.review_restaurant_name = None # Close review form
                        st.session_state.add_menu_for_restaurant = None # Close menu form
                        st.rerun()
                    
                # Display the 'Upload Menu' form if the button was clicked
                if st.session_state.add_menu_for_restaurant == row['Name']:
                    with st.container(border=True):
                        st.markdown(f"**Upload a new menu for {row['Name']}:**")
                        uploaded_menu_file = st.file_uploader(
                            "Upload a menu file (PDF or Image)",
                            type=["pdf", "png", "jpg", "jpeg"],
                            key=f"menu_uploader_{row['Name']}"
                        )

                        upload_col, cancel_col = st.columns(2)
                        with upload_col:
                            if st.button("Upload File", key=f"submit_menu_upload_{row['Name']}"):
                                if uploaded_menu_file is not None:
                                    try:
                                        file_bytes = uploaded_menu_file.getvalue()
                                        base64_data = base64.b64encode(file_bytes).decode('utf-8')
                                        file_name = uploaded_menu_file.name
                                        file_type = uploaded_menu_file.type

                                        if add_menu_item_to_csv(row['Name'], file_name, file_type, base64_data):
                                            st.success(f"Menu '{file_name}' uploaded successfully to {row['Name']}!", icon="✅")
                                            st.session_state.add_menu_for_restaurant = None
                                            st.cache_data.clear()
                                            time.sleep(2)
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error processing file: {e}")
                                else:
                                    st.warning("Please select a file to upload.", icon="⚠️")
                        with cancel_col:
                            if st.button("Cancel Upload", key=f"cancel_menu_upload_{row['Name']}"):
                                st.session_state.add_menu_for_restaurant = None
                                st.rerun()

                # Display the 'Upload Photo' form if the button was clicked
                if st.session_state.add_photo_for_restaurant == row['Name']:
                    with st.container(border=True):
                        st.markdown(f"**Upload a new photo for {row['Name']}:**")
                        uploaded_photo_file = st.file_uploader(
                            "Upload a photo (PNG, JPG, JPEG)",
                            type=["png", "jpg", "jpeg"],
                            key=f"photo_uploader_{row['Name']}"
                        )
                            
                        upload_col, cancel_col = st.columns(2)
                        with upload_col:
                            if st.button("Upload Photo", key=f"submit_photo_upload_{row['Name']}"):
                                if uploaded_photo_file is not None:
                                    try:
                                        file_bytes = uploaded_photo_file.getvalue()
                                        base64_data = base64.b64encode(file_bytes).decode('utf-8')
                                        file_name = uploaded_photo_file.name
                                        file_type = uploaded_photo_file.type

                                        if add_gallery_image_to_csv(row['Name'], file_name, file_type, base64_data):
                                            st.success(f"Photo '{file_name}' uploaded successfully to {row['Name']}'s gallery!", icon="✅")
                                            st.session_state.add_photo_for_restaurant = None
                                            st.cache_data.clear()
                                            time.sleep(2)
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error processing file: {e}")
                                else:
                                    st.warning("Please select a file to upload.", icon="⚠️")
                        with cancel_col:
                            if st.button("Cancel Upload", key=f"cancel_photo_upload_{row['Name']}"):
                                st.session_state.add_photo_for_restaurant = None
                                st.rerun()

                # Display the 'Submit Review' form if the button was clicked
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

                with st.expander(f"Past Curated Menus"):
                    menus = load_menus_from_csv(row['Name'])
                    if menus:
                        menu_cols = st.columns(3)
                        menu_col_index = 0
                        for menu in menus:
                            with menu_cols[menu_col_index]:
                                file_type = menu.get('file_type')
                                base64_data = menu.get('base64_data')

                                # Safely check for file type before processing
                                if file_type and isinstance(file_type, str) and file_type.startswith('image/'):
                                    st.write(f"**{menu.get('file_name', 'Menu File')}**")
                                    st.image(f"data:{file_type};base64,{base64_data}", use_container_width=True)
                                # Also apply the same check for PDF files
                                elif file_type and isinstance(file_type, str) and file_type == 'application/pdf':
                                    st.write(f"**{menu.get('file_name', 'Menu File')}**")
                                    # Create a download button for the PDF
                                    st.download_button(
                                        label="Download PDF",
                                        data=base64.b64decode(base64_data),
                                        file_name=menu.get('file_name', 'menu.pdf'),
                                        mime="application/pdf",
                                        key=f"download_{menu.get('file_name', 'menu')}_{row['Name']}"
                                    )
                                else:
                                    # Handle cases where file_type is None or an unsupported format
                                    st.warning(f"Could not display '{menu.get('file_name', 'Menu File')}'. Unsupported file type or missing data.")
                            menu_col_index = (menu_col_index + 1) % 3
                    else:
                        st.info("No curated menus uploaded for this restaurant.")
                    
                with st.expander(f"Past Reviews for {row['Name']}"):
                    reviews = load_reviews_from_csv(row['Name'])
                    if reviews:
                        for review in reviews:
                            # Safely handle the rating to avoid the float format error
                            review_rating = review.get('rating', 'N/A')
                            if isinstance(review_rating, (int, float)):
                                review_rating_str = f"{review_rating:.1f}"
                            else:
                                review_rating_str = str(review_rating)
                                    
                            st.markdown(f"**Rating:** {review_rating_str} ⭐")
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
    <p style="text-align: center; color: #999; font-size: 0.8em; font-family: \'Inter\', sans-serif;">
        Built with ❤️ using Streamlit.
    </p>
    """,
    unsafe_allow_html=True
)