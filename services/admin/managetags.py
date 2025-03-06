from __init__ import db
from models import Tag, UserTags, Users
from sqlalchemy.exc import SQLAlchemyError

def get_tags():
    try:
        tags = db.session.query(Tag.tag_id, Tag.name, Tag.admin_id).all()
        
        if not tags:
            return {"message": "No tags found"}
        
        return [
            {"tag_id": tag.tag_id, "name": tag.name, "admin_id": tag.admin_id}
            for tag in tags
        ]
    except Exception as e:
        db.session.rollback()
        print(f"Error fetching tags: {e}")
        return {"error": str(e)}

def get_tag_by_id(tag_id):
    try:
        tag = db.session.query(Tag.tag_id, Tag.name, Tag.admin_id).filter(Tag.tag_id == tag_id).first()

        if tag:
            return {"tag_id": tag.tag_id, "name": tag.name, "admin_id": tag.admin_id}
        else:
            return {"error": "Tag not found"}
    except Exception as e:
        db.session.rollback()
        print(f"Error fetching tag by id: {e}")
        return {"error": str(e)}

def add_tag(name, admin_id=None):
    try:
        if admin_id:
            new_tag = Tag(name=name, admin_id=admin_id)
        else:
            new_tag = Tag(name=name, admin_id=None)
        
        db.session.add(new_tag)
        db.session.commit()

        return {"tag_id": new_tag.tag_id, "name": new_tag.name, "admin_id": new_tag.admin_id}
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error adding tag: {e}")
        return {"error": "Failed to add tag"}


def update_tag(tag_id, name):
    try:
        tag = db.session.query(Tag).filter(Tag.tag_id == tag_id).first()

        if not tag:
            return {"error": "Tag not found"}

        tag.name = name
        db.session.commit()

        return {"tag_id": tag.tag_id, "name": tag.name}
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error updating tag: {e}")
        return {"error": str(e)}

def delete_tag(tag_id):
    try:
        tag = db.session.query(Tag).filter(Tag.tag_id == tag_id).first()

        if not tag:
            return {"error": "Tag not found"}

        db.session.query(UserTags).filter(UserTags.tag_id == tag_id).delete()

        db.session.delete(tag)
        db.session.commit()

        return {"message": "Tag deleted successfully"}
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting tag: {e}")
        return {"error": str(e)}

def add_tag_for_user(user_id, tag_id):
    try:
        user_tag = UserTags(user_id=user_id, tag_id=tag_id)
        db.session.add(user_tag)
        db.session.commit()

        return {"message": "Tag added successfully"}

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error adding tag for user: {e}")
        return {"error": str(e)}

def delete_tag_for_user(user_id, tag_id):
    try:
        tag = db.session.query(Tag).filter(Tag.tag_id == tag_id).first()
        if not tag:
            return {"error": "Tag not found"}

        user = db.session.query(Users).filter(Users.user_id == user_id).first()
        if not user:
            return {"error": "User not found"}

        user_tag = db.session.query(UserTags).filter_by(user_id=user_id, tag_id=tag_id).first()
        if not user_tag:
            return {"error": "Tag is not associated with this user"}

        db.session.delete(user_tag)
        db.session.commit()

        return {"message": "Tag removed successfully from user", "user_id": user_id, "tag_id": tag_id}

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting tag for user: {e}")
        return {"error": "Failed to delete tag for user"}

def get_tags_for_user(username):
    try:
        user = db.session.query(Users).filter(Users.username == username).first()
        
        if not user:
            return {"error": "User not found"}
        
        user_tags = db.session.query(UserTags.tag_id).filter(UserTags.user_id == user.user_id).all()

        if not user_tags:
            return []

        tags = db.session.query(Tag.tag_id, Tag.name).filter(Tag.tag_id.in_([tag_id for (tag_id,) in user_tags])).all()

        return [
            {"tag_id": tag.tag_id, "name": tag.name}
            for tag in tags
        ]
    
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error fetching tags for user: {e}")
        return {"error": str(e)}



