import streamlit as st
import requests
import os
import pandas as pd

# RapidAPI Configuration
RAPIDAPI_HOST = "instagram-scraper-api2.p.rapidapi.com"
RAPIDAPI_KEY = "1c1945f03emsh1a3b86f3327e4dep161688jsnd0e6c5d24c22"

def fetch_instagram_data(username):
    """
    Fetch Instagram data for a given username with comprehensive error handling
    """
    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }

    profile_data = None
    posts_data = None
    followers_data = None

    try:
        # Fetch profile info
        profile_url = f"https://{RAPIDAPI_HOST}/v1/info?username_or_id_or_url={username}"
        profile_response = requests.get(profile_url, headers=headers, timeout=10)
        if profile_response.status_code != 200:
            st.error(f"Failed to fetch profile. Status code: {profile_response.status_code}")
            return None, None, None

        profile_data = profile_response.json().get('data', {})

        if profile_data.get('is_private', True):
            st.error("The account is private and cannot be fetched.")
            return None, None, None

        # Fetch posts
        posts_url = f"https://{RAPIDAPI_HOST}/v1.2/posts?username_or_id_or_url={username}"
        posts_response = requests.get(posts_url, headers=headers, timeout=10)
        if posts_response.status_code != 200:
            st.error(f"Failed to fetch posts. Status code: {posts_response.status_code}")
            return profile_data, None, None

        posts_data = posts_response.json().get('data', {})

        # Fetch followers
        followers_url = f"https://{RAPIDAPI_HOST}/v1/following?username_or_id_or_url={username}"
        followers_response = requests.get(followers_url, headers=headers, timeout=10)
        if followers_response.status_code != 200:
            st.error(f"Failed to fetch followers. Status code: {followers_response.status_code}")
            return profile_data, posts_data, None

        followers_data = followers_response.json().get('data', {})
        return profile_data, posts_data, followers_data

    except requests.RequestException as e:
        st.error(f"Network error occurred: {e}")
        return None, None, None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None, None, None

def download_profile_picture(profile_pic_url):
    """
    Downloads the profile picture from the given URL and saves it locally.
    """
    try:
        os.makedirs("downloads/profile", exist_ok=True)
        response = requests.get(profile_pic_url, timeout=10)
        if response.status_code == 200:
            filename = "downloads/profile/profile_pic.jpg"
            with open(filename, 'wb') as file:
                file.write(response.content)
            return filename
        else:
            st.warning(f"Failed to download profile picture. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        st.error(f"Error downloading profile picture: {e}")
        return None

def download_posts(posts_data):
    """
    Download post images with robust error handling
    """
    downloaded_posts = []
    captions = []

    if not posts_data:
        st.warning("No post data available to download.")
        return [], []

    try:
        items = posts_data.get('items', [])
        if not items:
            st.warning("No posts found for this account.")
            return [], []

        os.makedirs("downloads/posts", exist_ok=True)
        for index, item in enumerate(items[:10]):
            image_versions = item.get('image_versions', {}).get('items', [])
            if image_versions:
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
    st.title("Instagram Profile Scraper")
    username = st.text_input("Enter Instagram Username")
    
    if st.button("Fetch Profile"):
        if username:
            with st.spinner('Fetching Instagram data...'):
                profile_data, posts_data, followers_data = fetch_instagram_data(username)
            
            if profile_data is None:
                st.error("Failed to fetch profile data. Please check the username and try again.")
                return

            st.header("Profile Details")
            col1, col2 = st.columns(2)
            with col1:
                profile_pic_url = profile_data.get('hd_profile_pic_url_info', {}).get('url')
                if profile_pic_url:
                    profile_pic_path = download_profile_picture(profile_pic_url)
                    if profile_pic_path:
                        st.image(profile_pic_path, width=200, caption="Profile Picture")
                    else:
                        st.warning("Could not download profile picture.")
                else:
                    st.warning("No profile picture URL found.")

            with col2:
                st.write(f"**Username:** {profile_data.get('username')}")
                st.write(f"**Full Name:** {profile_data.get('full_name')}")
                st.write(f"**Biography:** {profile_data.get('biography')}")
                st.write(f"**Followers:** {profile_data.get('follower_count')}")
                st.write(f"**Following:** {profile_data.get('following_count')}")
                

            st.subheader("Post Images")
            if posts_data:
                downloaded_posts, post_captions = download_posts(posts_data)
                if downloaded_posts:
                    st.image(downloaded_posts, width=200, caption=post_captions)
                else:
                    st.warning("No posts could be displayed")
            else:
                st.error("No post data available to download")

            st.subheader("Followers")
            if followers_data:
                followers_list = followers_data.get('items', [])
                followers_df = pd.DataFrame([
                    {
                        "Full Name": follower.get('full_name', 'N/A'),
                        "Username": follower.get('username', 'N/A'),
                        "Private Account": follower.get('is_private', 'N/A')
                    } for follower in followers_list
                ])
                st.dataframe(followers_df)
            else:
                st.warning("No followers data available")

if __name__ == "__main__":
    main()
