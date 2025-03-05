import os
from __init__ import create_app
from routes.competition import competition_bp

app = create_app()

# Register blueprints
app.register_blueprint(competition_bp, url_prefix='/api/competition')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5328)))

