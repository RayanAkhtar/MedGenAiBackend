from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth, credentials
import os

print("Starting middleware/auth.py initialization")

# Initialize Firebase Admin SDK
try:
    print("Attempting to initialize Firebase Admin SDK")
    cred = credentials.Certificate('medgenaifirebase.json')
    firebase_admin.initialize_app(cred)
    print("Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {str(e)}")


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("Starting require_auth decorator")
        auth_header = request.headers.get('Authorization')
        print(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith('Bearer '):
            print("No valid Authorization header found")
            return jsonify({'error': 'No token provided'}), 401
            
        token = auth_header.split('Bearer ')[1]
        print(f"Extracted token: {token[:10]}...")  # Only print first 10 chars for security
        
        try:
            print("Attempting to verify ID token")
            # Add clock tolerance of 5 seconds
            decoded_token = auth.verify_id_token(
                token,
                clock_skew_seconds=5  # Add this parameter
            )
            print(f"Token verified successfully. UID: {decoded_token['uid']}")
            request.user_id = decoded_token['uid']
            return f(*args, **kwargs)
        except Exception as e:
            print(f"Auth error: {str(e)}")  # Debug print
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
            
    return decorated_function
from flask import Blueprint, request, jsonify
from firebase_admin import auth
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/session', methods=['POST'])
def create_session():
    print("Starting create_session function")
    try:
        # Get the ID token from the request
        print("Attempting to get ID token from request")
        id_token = request.json.get('idToken')
        if not id_token:
            print("No ID token provided in request")
            return jsonify({'error': 'No ID token provided'}), 400

        print("Setting up session parameters")
        # Verify the ID token and create a session cookie
        # Set session expiration to 5 days
        expires_in = datetime.timedelta(days=5)
        
        print("Attempting to create session cookie")
        # Create the session cookie using Firebase Admin SDK
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
        print("Session cookie created successfully")
        
        response = jsonify({'sessionCookie': session_cookie})
        print("Returning successful response")
        
        return response, 200

    except Exception as e:
        print(f"Error in create_session: {str(e)}")
        return jsonify({'error': str(e)}), 401
