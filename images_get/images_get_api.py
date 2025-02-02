from flask import Flask, jsonify, url_for
import os
from dotenv import load_dotenv


# NOTE: CREATE A .env file in this folder and fill it in with the following variables: IMAGE_FOLDER, PORT, HOST and VM_IP
# FOR TESTING: run file and GET Request from http://127.0.0.1:5000/fetchImages/

load_dotenv()

IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', 'static/images')
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
VM_IP = os.getenv('VM_IP',f"http://{HOST}:{PORT}" )

app = Flask(__name__)

@app.route('/fetchImages/',  methods=['GET'])
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
        image_urls = [ VM_IP + f"/{IMAGE_FOLDER}/{type}/{image}" for image in images_offsetted]
        return jsonify({'new_offset': offset + size, f'images': image_urls})
    except Exception:
        return jsonify({'error': 'No images found'}), 400

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)

