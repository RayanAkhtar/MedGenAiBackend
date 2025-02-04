from flask import Flask, jsonify, url_for, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from urllib.parse import unquote

# NOTE: CREATE A .env file in this folder and fill it in with the following variables: IMAGE_FOLDER, PORT, HOST, and VM_IP
# FOR TESTING: run file and GET Request from http://127.0.0.1:5000/fetchImages/

load_dotenv()

IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', 'static/images')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
VM_IP = os.getenv('VM_IP', f"http://{HOST}:{PORT}")

app = Flask(__name__)
CORS(app)

@app.route('/fetchImages/', methods=['GET'])
@app.route('/fetchImages/<type>', defaults={'offset': 0, 'size': 5}, methods=['GET'])
@app.route('/fetchImages/<type>/<int:offset>', defaults={'size': 5}, methods=['GET'])
@app.route('/fetchImages/<type>/<int:offset>/<int:size>', methods=['GET'])
def get_images(offset=0, type='real', size=5):
    if offset is None:
        offset = 0
    try:
        offset = int(offset)
    except ValueError:
        return jsonify({'error': 'Invalid offset value'}), 400
    try:
        images = sorted(os.listdir(f"{IMAGE_FOLDER}/{type}"))
        if offset + size >= len(images):
            offset = 0
        images_offsetted = images[offset:offset + size]
        image_urls = [VM_IP + f"/{IMAGE_FOLDER}/{type}/{image}" for image in images_offsetted]
        return jsonify({'new_offset': offset + size, 'images': image_urls})
    except Exception:
        return jsonify({'error': 'No images found'}), 400

# New route to fetch an image by its ID or path
@app.route('/fetchImageById/<image_id>', methods=['GET'])
@app.route('/fetchImageByPath/<path:image_path>', methods=['GET'])
def get_image_by_id_or_path(image_id=None, image_path=None):
    try:
        if image_id:
            # You may want to implement logic to map image_id to a file path in your system.
            image_file = f"{IMAGE_FOLDER}/{image_id}"  # Assuming a .jpg extension for simplicity.
        elif image_path:
            # If the image path is passed, use it directly.
            image_file = f"{IMAGE_FOLDER}/{image_path}"
        else:
            return jsonify({'error': 'No image ID or path provided'}), 400

        # Ensure the image exists
        print("image_file", image_file)
        if os.path.exists(image_file):
            print("aaaaa")
            return send_from_directory(os.path.dirname(image_file), os.path.basename(image_file))
        else:
            print("bbbbb")
            return jsonify({'error': 'Image not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)

