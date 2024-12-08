from flask import Flask, render_template, request, jsonify
import requests
import os
import json

app = Flask(__name__)

RAPIDAPI_HOST = "instagram-scraper-api2.p.rapidapi.com"
RAPIDAPI_KEY = "1c1945f03emsh1a3b86f3327e4dep161688jsnd0e6c5d24c22"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/fetch', methods=['POST', 'GET'])
def fetch_data():
    username = request.form['username']
    Data = 'static/Data'

    headers = {
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY,
    }

    profile_url = f"https://{RAPIDAPI_HOST}/v1/info?username_or_id_or_url={username}"
    posts_url = f"https://{RAPIDAPI_HOST}/v1.2/posts?username_or_id_or_url={username}"
    followers_url =  f"https://{RAPIDAPI_HOST}/v1/following?username_or_id_or_url={username}"

    profile_response = requests.get(profile_url, headers=headers)
    posts_response = requests.get(posts_url, headers=headers)
    following_response = requests.get(followers_url, headers=headers)

    if profile_response.status_code != 200:
        error_message = f"Error: {profile_response.json().get('message', 'Unable to fetch data.')}"

        # Return the error in the response template
        return render_template('index.html', error=error_message)

    profile_data = profile_response.json().get('data', {})
    posts_data = posts_response.json().get('data', {})
    follower_data = following_response.json().get('data', {})

###################################################################################################################
    data =  follower_data.get('items', {})
    followers_list = []
    for follower in data:
        full_name = follower.get('full_name', 'N/A')
        username = follower.get('username', 'N/A')
        is_private = follower.get('is_private', 'N/A')
        followers_list.append({"full_name": full_name, "username": username, "is_private": is_private})

    os.makedirs(Data, exist_ok=True)  # Ensure the Data folder exists
    file_path = os.path.join(Data, 'followers.json')

    with open(file_path, 'w', encoding='utf-8') as file:
         json.dump(followers_list, file, indent=4, ensure_ascii=False)

##################################################################################################################

    items = posts_data.get('items', [])
    save_folder = 'static/images/posts'
    os.makedirs(save_folder, exist_ok=True)
    for index, item in enumerate(items):
        # Check if image versions exist in the response
        image_versions = item.get('image_versions', {}).get('items', [])
        for image in image_versions:
            image_url = image.get('url', None)
            if image_url:
                # Download and save the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_filename = f"{save_folder}/post_image_{index}.jpg"
                    with open(image_filename, 'wb') as file:
                        file.write(response.content)
                    print(f"Image saved: {image_filename}")
                else:
                    print(f"Failed to download image: {image_url}")


    image_directory = os.path.join('static', 'images', 'posts')
    try:
        image_files = os.listdir(image_directory)
    except FileNotFoundError:
        image_files = []

    image_url = profile_data.get('hd_profile_pic_url_info', {}).get('url', 'URL not found')
    # Path where you want to save the image
    save_path = 'static/images/downloaded_image.jpg'

    # Create the 'images' directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Download and save the image
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print('Image saved successfully!')
    else:
        print(f'Failed to download image. Status code: {response.status_code}')

    if profile_data.get('is_private', True):
        return render_template('index.html', error="The account is private and cannot be fetched.")

    return render_template(
        'index.html',
        profile=profile_data,  # Pass profile data to the template
        posts=posts_data,  # Pass posts data to the template
        image_files=image_files,
    )
@app.route("/following")
def show_followers():
    data_folder = os.path.join(os.getcwd(), "static/Data")
    file_path = os.path.join(data_folder, "followers.json")
    
    if os.path.exists(file_path):
       with open(file_path, "r", encoding="utf-8") as file:
         followers = json.load(file)
    else:
        followers = []

    return render_template("followers.html", followers=followers)


if __name__ == '__main__':
    app.run(debug=True)
