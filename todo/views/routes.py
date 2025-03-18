from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta
 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})

@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    paramsCompeleted  = request.args.get('completed', default = None)
    if(paramsCompeleted):
        if(paramsCompeleted.lower() == 'true'):
            paramsCompeleted = True
        else:
            paramsCompeleted = False
    paramsWindow  = request.args.get('window', default = None, type = int)
   
    if(paramsWindow):
        nowtime = (datetime.now() + timedelta(days=paramsWindow)).strftime("%Y-%m-%dT00:00:00")
        
       

    result = []
    for todo in todos:

        if(paramsCompeleted is not None and todo.completed != paramsCompeleted):
            continue

        if(paramsWindow is not None and todo.deadline_at and str(todo.deadline_at) > nowtime):
            continue

        result.append(todo.to_dict())

    
    return jsonify(result)


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST'])
def create_todo():
      # 不能更新 title 为 NULL
    if request.json.get('title') is None:
        return jsonify({'error': 'input title'}), 400
    allowed_fields = {'title', 'description', 'completed', 'deadline_at'}
    # 检查是否包含额外字段
    extra_fields = set(request.json.keys()) - allowed_fields
    if extra_fields:
        return jsonify({'error': 'Extra fields are not allowed', 'fields': list(extra_fields)}), 400

    todo = Todo(
    title=request.json.get('title'),
    description=request.json.get('description'),
    completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    # Adds a new record to the database or will update an existing record.
    db.session.add(todo)
    # Commits the changes to the database.
    # This must be called for the changes to be saved.
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
      # 防止修改 ID
    if 'id' in request.json and request.json['id'] != todo_id:
        return jsonify({'error': 'ID cannot be changed'}), 400
    # 允许的字段
    allowed_fields = {'title', 'description', 'completed', 'deadline_at'}

    # 检查是否包含额外字段
    extra_fields = set(request.json.keys()) - allowed_fields
    if extra_fields:
        return jsonify({'error': 'Extra fields are not allowed', 'fields': list(extra_fields)}), 400
    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()
    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({}), 200
    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200

 
