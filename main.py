from flask import Flask, jsonify, render_template, request
from psql import PostgreSqlDB

flask_app = Flask(__name__, template_folder='templates', static_folder='static')

db = PostgreSqlDB("python")
db.connection()

TABLE_NAME = "projes"

db.create_table(TABLE_NAME, "id SERIAL PRIMARY KEY, name VARCHAR(100), status BOOLEAN, language VARCHAR(50), description VARCHAR(255)")


@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/api/projects', methods=['GET'])
def get_projects():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', 'all', type=str)

    all_projects = db.select_rows(TABLE_NAME)
    
    if not all_projects:
        return jsonify({
            'projects': [],
            'total_pages': 0,
            'current_page': page
        })
    
    if search:
        all_projects = [p for p in all_projects if search.lower() in p[1].lower()] 

    if status_filter == 'completed':
        all_projects = [p for p in all_projects if p[2] == True]
    elif status_filter == 'pending':
        all_projects = [p for p in all_projects if p[2] == False]
    
    items_per_page = 2 
    total_items = len(all_projects)
    
    total_pages = (total_items + items_per_page - 1) // items_per_page if total_items > 0 else 1
    
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages 

    start = (page - 1) * items_per_page
    end = start + items_per_page
    projects_page = all_projects[start:end]
    
    
    return jsonify({
        'projects': [{'id': p[0], 'name': p[1], 'language': p[3], 'description': p[4], 'status': p[2]} for p in projects_page],
        'total_pages': total_pages,
        'current_page': page
    })

@flask_app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Proje adı gerekli'}), 400
    
    new_project = {
        "name": data['name'], 
        "language": data.get('language', ''),
        "description": data.get('description', ''),
        "status": False 
    }
    db.insert_record(TABLE_NAME, new_project)
    
    return jsonify({'message': 'Proje eklendi'}), 201


@flask_app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    project = db.select_row(TABLE_NAME, {"id": project_id})
    
    if not project:
        return jsonify({'error': 'Proje bulunamadı'}), 404
    
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Proje adı gerekli'}), 400

    update_data = {
        "name": data['name'], 
        "language": data.get('language', ''),
        "description": data.get('description', '')
    }
    
    db.update_record(TABLE_NAME, update_data, {"id": project_id})
    
    return jsonify({'message': 'Proje güncellendi'}), 200


@flask_app.route('/api/projects/<int:project_id>/toggle-status', methods=['PUT'])
def toggle_project_status(project_id):
    project = db.select_row(TABLE_NAME, {"id": project_id})
    
    if not project:
        return jsonify({'error': 'Proje bulunamadı'}), 404
    
    
    new_status = not project[2] 
    
    db.update_record(TABLE_NAME, {"status": new_status}, {"id": project_id})
    
    
    return jsonify({'id': project_id, 'name': project[1], 'status': new_status}), 200


@flask_app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = db.select_row(TABLE_NAME, {"id": project_id})
    
    if not project:
        return jsonify({'error': 'Proje bulunamadı'}), 404
    
    db.delete_record(TABLE_NAME, {"id": project_id})
    
    db.restart_identity_to_one(TABLE_NAME,"id")
    
    return jsonify({'message': 'Proje silindi'}), 200

if __name__ == '__main__':
    flask_app.run(debug=True,host='0.0.0.0', port=5000)
