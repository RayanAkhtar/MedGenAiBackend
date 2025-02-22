from flask import jsonify, send_from_directory, Blueprint
import os
from __init__ import db
from sqlalchemy import text
from services.admin.admin import get_metadata_counts

from routes.admin.admin import bp

# TODO: move some of this to services for simplicity

def fetch_data_for_csv(table_name):
    try:
        query = text(f"SELECT * FROM {table_name}")
        
        result = db.session.execute(query)
        db.session.commit()

        columns = result.keys()

        rows = result.fetchall()

        data = [dict(zip(columns, row)) for row in rows]

        return data

    except Exception as e:
        db.session.rollback()
        raise Exception(f"Error fetching data for table {table_name}: {e}")


def convert_to_csv(data):
    if not data:
        return "No data available"
    header = data[0].keys()
    rows = [','.join(str(value) for value in row.values()) for row in data]
    csv_data = ','.join(header) + '\n' + '\n'.join(rows)
    return csv_data

@bp.route('/admin/downloadFeedbackData', methods=['GET'])
def download_feedback_data():
    try:
        if not os.path.exists('./downloads'):
            os.makedirs('./downloads')

        data = fetch_data_for_csv('feedback')
        csv_data = convert_to_csv(data)
        file_path = './downloads/feedback_data.csv'

        with open(file_path, 'w') as file:
            file.write(csv_data)

        print("wrote the file")

        return send_from_directory('downloads', 'feedback_data.csv', as_attachment=True)

    except Exception as e:
        print("exception", e)
        return str(e), 500
    


@bp.route('/admin/downloadImageData', methods=['GET'])
def download_image_data():
    try:
        data = fetch_data_for_csv('images')
        csv_data = convert_to_csv(data)
        file_path = os.path.join('downloads', 'image_data.csv')

        with open(file_path, 'w') as file:
            file.write(csv_data)

        return send_from_directory('downloads', 'image_data.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/downloadLeaderboard', methods=['GET'])
def download_leaderboard_data():
    try:
        data = fetch_data_for_csv('users')
        csv_data = convert_to_csv(data)
        file_path = os.path.join('downloads', 'leaderboard_data.csv')

        with open(file_path, 'w') as file:
            file.write(csv_data)

        return send_from_directory('downloads', 'leaderboard_data.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/admin/downloadCompetitionData', methods=['GET'])
def download_competition_data():
    try:
        data = fetch_data_for_csv('competitions')
        csv_data = convert_to_csv(data)
        file_path = os.path.join('downloads', 'competition_data.csv')

        with open(file_path, 'w') as file:
            file.write(csv_data)

        return send_from_directory('downloads', 'competition_data.csv', as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@bp.route('/admin/feedbackCount', methods=['GET'])
def feedback_count():
    try:
        count = get_metadata_counts().get('feedback', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/imageCount', methods=['GET'])
def image_count():
    try:
        count = get_metadata_counts().get('image', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/leaderboardCount', methods=['GET'])
def leaderboard_count():
    try:
        count = get_metadata_counts().get('leaderboard', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/admin/competitionCount', methods=['GET'])
def competition_count():
    try:
        count = get_metadata_counts().get('competition', 0)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    