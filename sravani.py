from flask import Flask, render_template, redirect, url_for, request, flash, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
import base64
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_file
from PIL import Image
from io import BytesIO
import os
from flask import jsonify
import requests
from flask import send_from_directory
import cv2
import moviepy
from moviepy.editor import VideoFileClip, AudioFileClip,ImageSequenceClip








app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'buddi1234.',
    'database': 'sat',
}

def connect_to_database():
    return mysql.connector.connect(**db_config)

def get_db():
    if 'db' not in g:
        g.db = connect_to_database()
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    with db.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM authentication WHERE id=%s", (user_id,))
        user_data = cursor.fetchone()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['password'])
    return None

def delete_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

@app.route('/')
def home():
    images_folder = os.path.join(app.static_folder, 'images')
    if os.path.exists(images_folder):
        delete_files_in_directory(images_folder)
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email=request.form['email']
        db = get_db()
        with db.cursor() as cur:
            q1 = "SELECT * FROM authentication WHERE username=%s;"
            cur.execute(q1,(username,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Username already exists. Choose a different one.', 'error')
            else:
                #hashed_password = generate_password_hash(password, method='sha256')
                cur.execute("INSERT INTO authentication (username, password, email) VALUES (%s, %s, %s)", (username, password, email))                
                db.commit()
                flash('Account created successfully. Please log in.', 'success')
                return render_template('signin.html')

    return render_template('signup.html')

# Function to delete all files in a directory



@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            return redirect(url_for('admin'))

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM authentication WHERE username=%s", (username,))
            user_data = cursor.fetchone()

        if user_data and user_data[3] == password:
            user = User(user_data[0], user_data[1], user_data[3])
            login_user(user)
            flash('Login successful!', 'success')

            # Fetch images associated with the logged-in user
            with db.cursor() as cursor:
                cursor.execute("SELECT data FROM images WHERE user_id=%s", (user.id,))
                rows = cursor.fetchall()
                image_list = []  # Initialize image_list here
                for i, row in enumerate(rows):
                    image_data = row[0]
                    image = Image.open(BytesIO(image_data))
                    image.save(f'static/images/{i}.png')
                    image_dir = os.path.join(app.static_folder, 'images')
                    image_list.append(f'{i}.png')  # Append image file name to image_list
                saved_images_folder = os.path.join(app.static_folder, 'saved_images')
                if os.path.exists(saved_images_folder):
                    delete_files_in_directory(saved_images_folder)    
                return render_template('upload.html', image_list=image_list)
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('signin.html')

@app.route('/admin')
def admin():
    # Fetch all data from the authentication table
   db = get_db()
   with db.cursor() as cursor:
    cursor.execute("SELECT * FROM authentication WHERE username != 'admin'")
    all_users_data = cursor.fetchall()


    return render_template('admin.html', users=all_users_data)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        form_data = request.files
        uploaded_images = form_data.getlist('images')

        db = get_db()
        save_images_to_database(uploaded_images, db)

        return redirect(url_for('customize'))

    # Render the upload page
    return render_template('upload.html')

def save_images_to_database(uploaded_images, db_connection):
    try:
        cursor = db_connection.cursor()

        # Create the
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                USER_ID INT,
                DATA LONGBLOB
            )
        """)

        # Save each image to the database as a BLOB
        for image in uploaded_images:
            img_data = image.read()
            cursor.execute("""
                INSERT INTO images (USER_ID, DATA)
                VALUES (%s, %s)
            """, (current_user.id, img_data))

        # Commit the changes
        db_connection.commit()

    except mysql.connector.Error as e:
        print("Error occurred:", e)

    finally:
        # Close the cursor and the database connection
        cursor.close()
        db_connection.close()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return render_template('signin.html')

@app.route('/back')
@login_required
def goback():
    db=get_db()
    with db.cursor() as cursor:
                cursor.execute("SELECT data FROM images WHERE user_id=%s", (current_user.id,))
                rows = cursor.fetchall()
                image_list = []  # Initialize image_list here
                for i, row in enumerate(rows):
                    image_data = row[0]
                    image = Image.open(BytesIO(image_data))
                    image.save(f'static/images/{i}.png')
                    image_dir = os.path.join(app.static_folder, 'images')
                    image_list.append(f'{i}.png')  # Append image file name to image_list
                saved_images_folder = os.path.join(app.static_folder, 'saved_images')
                if os.path.exists(saved_images_folder):
                    delete_files_in_directory(saved_images_folder)    
                return render_template('upload.html', image_list=image_list)

   

@app.route('/customize')
@login_required
def customize():
    flash('Successfull.', 'info')
    return render_template('video_customize.html') 

@app.route('/preview', methods=['POST'])
@login_required
def preview():
    duration_per_image = int(request.form['imageDuration'])
    background_music = request.form['backgroundMusic']
    resolution = request.form['resolution'] 

    # Trigger video generation here
    generate_video(duration_per_image,background_music,resolution)

    flash('Successfully generated video.', 'info')
    return render_template('preview.html')

@app.route('/get_images')
@login_required
def get_images():
    images_folder = os.path.join(app.static_folder, 'images')
    if os.path.exists(images_folder):
        delete_files_in_directory(images_folder)
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT data FROM images WHERE user_id=%s", (current_user.id,))
        rows = cursor.fetchall()
        image_list = []  # Initialize image_list here
        for i, row in enumerate(rows):
            image_data = row[0]
            image = Image.open(BytesIO(image_data))
            image.save(f'static/images/{i}.png')
            image_dir = os.path.join(app.static_folder, 'images')
            image_list.append(f'{i}.png')  # Append image file name to image_list
        
        saved_images_folder = os.path.join(app.static_folder, 'saved_images')
        if os.path.exists(saved_images_folder):
            delete_files_in_directory(saved_images_folder)    
    
    image_folder = 'static/images'  # Path to your images folder
    image_files = os.listdir(image_folder)
    image_urls = [f'/static/images/{filename}' for filename in image_files]
    return jsonify(image_urls)


import os
from flask import request, jsonify

@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        data = request.json  # Get data from the request
        image_url = data.get('imageUrl')  # Extract image URL

        # Construct the absolute path to the image file
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Path to your Flask app directory
        image_relative_path = image_url.split('/static/')[-1]  # Extract relative path from the URL
        image_path = os.path.join(base_dir, 'static', image_relative_path)

        print("Image Path:", image_path)  # Debugging: Print out the image path

        if os.path.exists(image_path) and os.path.isfile(image_path):  # Check if the file exists and is a file
            # Define the directory where you want to save the image
            save_folder = os.path.join(base_dir, 'static', 'saved_images')

            # Create the directory if it doesn't exist
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            # Extract filename from the URL
            filename = os.path.basename(image_url)

            # Save the image to the 'saved_images' folder
            with open(os.path.join(save_folder, filename), 'wb') as f:
                with open(image_path, 'rb') as image_file:
                    f.write(image_file.read())

            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        # Log the error for debugging
        print("Error in save_image:", e)
        return jsonify({"error": "Internal Server Error"}), 500

# Route to serve the saved images
@app.route('/saved_images/<path:filename>')
def serve_saved_image(filename):
    return send_from_directory(os.path.join(app.static_folder, 'saved_images'), filename)

@app.route('/delete_image', methods=['POST'])
def delete_image():
    try:
        data = request.json  # Get data from the request
        filename = data.get('filename')  # Extract filename from the request

        if filename:
            # Construct the absolute path to the image file
            base_dir = os.path.dirname(os.path.abspath(__file__))  # Path to your Flask app directory
            image_path = os.path.join(base_dir, 'static', 'saved_images', filename)

            if os.path.exists(image_path) and os.path.isfile(image_path):  # Check if the file exists and is a file
                # Delete the image file
                os.remove(image_path)
                return jsonify({"success": True}), 200
            else:
                return jsonify({"error": "Image not found"}), 404
        else:
            return jsonify({"error": "Filename not provided"}), 400
    except Exception as e:
        # Log the error for debugging
        print("Error in delete_image:", e)
        return jsonify({"error": "Internal Server Error"}), 500

# Route to generate and serve the video





def generate_video(duration_per_image, background_music=None, resolution=720):
    try:
        # Define paths
        image_folder = os.path.join(app.static_folder, 'saved_images')
        video_path = os.path.join(app.static_folder, 'vid.mp4')
        video_path_with_audio = os.path.join(app.static_folder, 'vid_with_audio.mp4')

        # Get all image filenames
        image_files = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.endswith('.png')]
        
        print("Number of image files:", len(image_files))  # Debug statement

        # Define video settings
        fps = 30  # Frames per second

        # Create video clip
        video_clip = ImageSequenceClip(image_files, fps=fps)
        video_clip = video_clip.set_duration(len(image_files) * duration_per_image)
        video_clip = video_clip.resize(width=resolution)  # Apply resolution

        # Write video clip to file
        video_clip.write_videofile(video_path, codec='libx264', fps=fps)

        # Add background music if provided
        if background_music:
            print("Adding background music...")
            audio_clip = AudioFileClip(background_music)
            audio_clip = audio_clip.set_duration(video_clip.duration)
            video_clip = video_clip.set_audio(audio_clip)
            video_clip.write_videofile(video_path_with_audio, codec='libx264', fps=fps)

        return redirect(url_for('preview'))
    except Exception as e:
        print("Error generating video:", e)
        return jsonify({"error": "Internal Server Error"}), 500











# Route to serve the generated video

@app.route('/video')
def serve_video():
    video_path = os.path.join(app.static_folder, 'vid.mp4')
    return send_file(video_path)

if __name__ == '__main__':
    app.run(debug=True)
