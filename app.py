import streamlit as st
import requests
import os
import json
import pandas as pd

# RapidAPI Configuration
RAPIDAPI_HOST = "instagram-scraper-api2.p.rapidapi.com"
RAPIDAPI_KEY = "1c1945f03emsh1a3b86f3327e4dep161688jsnd0e6c5d24c22"

def fetch_instagram_data(username):
    """
    Fetch Instagram data for a given username
    """
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }

    try:
        # Fetch profile info
        profile_url = f"https://{RAPIDAPI_HOST}/v1/info?username_or_id_or_url={username}"
        profile_response = requests.get(profile_url, headers=headers)
        profile_response.raise_for_status()
        profile_data = profile_response.json().get('data', {})

        # Check if account is private
        if profile_data.get('is_private', True):
            st.error("The account is private and cannot be fetched.")
            return None, None, None

        # Fetch posts
        posts_url = f"https://{RAPIDAPI_HOST}/v1.2/posts?username_or_id_or_url={username}"
        posts_response = requests.get(posts_url, headers=headers)
        posts_response.raise_for_status()
        posts_data = posts_response.json().get('data', {})

        # Fetch followers
        followers_url = f"https://{RAPIDAPI_HOST}/v1/following?username_or_id_or_url={username}"
        followers_response = requests.get(followers_url, headers=headers)
        followers_response.raise_for_status()
        followers_data = followers_response.json().get('data', {})

        return profile_data, posts_data, followers_data

    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None, None, None

def download_profile_picture(profile_data):
    """
    Download profile picture
    """   
    try:
        image_url = profile_data.get('hd_profile_pic_url_info', {}).get('url')
        if image_url:
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Use a unique filename
            filename = f"profile_pic_{profile_data.get('username', 'unknown')}.jpg"
            filepath = os.path.join("downloads", filename)
            
            # Ensure downloads directory exists
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'wb') as file:
                file.write(response.content)
            
            return filepath
    except Exception as e:
        st.warning(f"Could not download profile picture: {e}")
        return None

def download_posts(posts_data):
    """
    Download post images
    """
    downloaded_posts = []
    captions = []
    if not posts_data:
        st.warning("No post data available.")
        return [], []

    try:
        items = posts_data.get('items', [])

          # Check if items list is empty
        if not items:
            st.warning("No posts found for this account.")
            return [], []
        
        os.makedirs("downloads/posts", exist_ok=True)
        
        for index, item in enumerate(items[:10]):
            image_versions = item.get('image_versions', {}).get('items', [])
            for img in image_versions:
                image_url = image_versions[0].get('url')
                if image_url:
                    try:
                        response = requests.get(image_url, timeout=10)
                        
                        if response.status_code == 200:
                            filename = f"downloads/posts/post_{index}.jpg"
                            with open(filename, 'wb') as file:
                                file.write(response.content)
                            
                            downloaded_posts.append(filename)
                            captions.append(f"Post {index + 1}")
                    except requests.RequestException as e:
                        st.warning(f"Could not download post {index + 1}: {e}")
    except Exception as e:
        st.error(f"Unexpected error in downloading posts: {e}")
        return [], []
    
    if downloaded_posts:
        st.info(f"Successfully downloaded {len(downloaded_posts)} posts")
    else:
        st.warning("No posts could be downloaded")

    return downloaded_posts, captions

def main():
    # ... (previous code remains the same)

    # Download and Display Posts
    st.subheader("Post Images")
    if posts_data:
        downloaded_posts, post_captions = download_posts(posts_data)
    
    # Display downloaded post images with matching captions
        if downloaded_posts:
            st.image(downloaded_posts, width=200, caption=post_captions)
        else:
            st.warning("No posts could be displayed")
    else:
        st.error("No post data available to download")
        
    st.title("Instagram Profile Scraper")
    
    # User input
    username = st.text_input("Enter Instagram Username")
    
    if st.button("Fetch Profile"):
        if username:
            # Fetch data
            with st.spinner('Fetching Instagram data...'):
                profile_data, posts_data, followers_data = fetch_instagram_data(username)
            
            if profile_data:
                # Display Profile Information
                st.header("Profile Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.image(profile_data.get('hd_profile_pic_url_info', {}).get('url'), 
                             width=200, 
                             caption="Profile Picture")
                
                with col2:
                    st.write(f"**Username:** {profile_data.get('username')}")
                    st.write(f"**Full Name:** {profile_data.get('full_name')}")
                    st.write(f"**Followers:** {profile_data.get('follower_count')}")
                    st.write(f"**Following:** {profile_data.get('following_count')}")
                
                # Download Profile Picture
                st.subheader("Downloads")
                profile_pic = download_profile_picture(profile_data)
                if profile_pic:
                    st.success(f"Profile Picture Downloaded: {profile_pic}")
                
                # Download and Display Posts
                st.subheader("Post Images")
                downloaded_posts = download_posts(posts_data)
                
                # Display downloaded post images
                if downloaded_posts:
                    st.image(downloaded_posts, width=200, caption="Downloaded Posts")
                
                # Followers List
                st.subheader("Followers")
                followers_list = followers_data.get('items', [])
                followers_df = pd.DataFrame([
                    {
                        "Full Name": follower.get('full_name', 'N/A'),
                        "Username": follower.get('username', 'N/A'),
                        "Private Account": follower.get('is_private', 'N/A')
                    } for follower in followers_list
                ])
                
                st.dataframe(followers_df)

if __name__ == "__main__":
    main()
