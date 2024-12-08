# InstaLook
InstaFetch is a sleek and efficient tool that allows users to fetch and display data from public Instagram accounts using their user IDs. Powered by Rapid API, it simplifies accessing public account information for analytics, insights, or personal use—all through a user-friendly interface.


# InstaFetch

**InstaFetch** is a Flask-based web application that allows users to fetch data from public Instagram accounts using a username or ID. The app utilizes the **RapidAPI Instagram Scraper API** to retrieve profile details, posts, and followers.

## Features
- Fetch public profile details including profile pictures.
- Retrieve recent posts with images and save them locally.
- Access a list of followers with details like username, full name, and privacy status.
- User-friendly interface to display fetched data dynamically.

## Prerequisites
- Python 3.7 or later
- Flask
- Requests
- A valid RapidAPI key for the Instagram Scraper API

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/InstaFetch.git
   cd InstaFetch


2. Install dependencies:

   > pip install -r requirements.txt

3. Set up your environment variables:

   > Add your RapidAPI key and host in app.py.

4. Start the application:
  > python app.py

5. Open your browser and navigate to:
   > http://127.0.0.1:5000/

