from flask import Flask

def create_app():
    app = Flask(__name__)

    # TODO: change to something else later, and ideally should hide this
    app.config['SECRET_KEY'] = "hello world" 

    return app