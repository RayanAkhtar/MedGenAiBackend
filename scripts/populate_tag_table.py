from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from __init__ import db, create_app

tags = ["Lung Legend", "Neuro Ninja", "X-Ray Visionary", "AI Antagonist", "Diagnosis Master", "AI Skeptic"]

def populate_tags():
    with db.session.begin():
        for tag in tags:
            existing_tag = db.session.execute(text("SELECT 1 FROM tag WHERE name = :tag"), {"tag": tag}).fetchone()
            if not existing_tag:
                db.session.execute(text("INSERT INTO tag (name) VALUES (:tag)"), {"tag": tag})
        db.session.commit()
        
if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        populate_tags()
        print("✅ Tag table populated successfully!")
