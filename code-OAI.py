from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.todo_db
todos_collection = db.todos

# Helper function to convert ObjectId to string
def todo_serializer(todo):
    return {
        '_id': str(todo['_id']),
        'title': todo['title'],
        'description': todo.get('description', ''),
        'completed': todo['completed']
    }

# Routes
@app.route('/todos', methods=['GET'])
def get_all_todos():
    todos = todos_collection.find()
    return jsonify([todo_serializer(todo) for todo in todos])

@app.route('/todo/<id>', methods=['GET'])
def get_todo(id):
    todo = todos_collection.find_one({'_id': ObjectId(id)})
    if todo:
        return jsonify(todo_serializer(todo))
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/todo', methods=['POST'])
def create_todo():
    data = request.get_json()
    new_todo = {
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': False
    }
    result = todos_collection.insert_one(new_todo)
    return jsonify(todo_serializer(todos_collection.find_one({'_id': result.inserted_id})))

@app.route('/todo/<id>', methods=['PUT'])
def update_todo(id):
    data = request.get_json()
    updated_todo = {
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': data['completed']
    }
    result = todos_collection.update_one({'_id': ObjectId(id)}, {'$set': updated_todo})
    if result.matched_count:
        return jsonify(todo_serializer(todos_collection.find_one({'_id': ObjectId(id)})))
    return jsonify({'error': 'Todo not found'}), 404

@app.route('/todo/<id>', methods=['DELETE'])
def delete_todo(id):
    result = todos_collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'message': 'Todo deleted'})
    return jsonify({'error': 'Todo not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)

