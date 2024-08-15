from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)

# MongoDB connection (Replace the connection string with your MongoDB URI)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/todo_db")
client = MongoClient(MONGO_URI)
db = client.todo_db
tasks_collection = db.tasks


@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    for task in tasks_collection.find():
        tasks.append({
            '_id': str(task['_id']),
            'title': task['title'],
            'description': task.get('description', ''),
            'completed': task['completed']
        })
    return jsonify(tasks)


@app.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks_collection.find_one({'_id': ObjectId(task_id)})
    if task:
        return jsonify({
            '_id': str(task['_id']),
            'title': task['title'],
            'description': task.get('description', ''),
            'completed': task['completed']
        })
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    if 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    task = {
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': False
    }
    result = tasks_collection.insert_one(task)
    task['_id'] = str(result.inserted_id)
    return jsonify(task), 201


@app.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    update_data = {}

    if 'title' in data:
        update_data['title'] = data['title']
    if 'description' in data:
        update_data['description'] = data['description']
    if 'completed' in data:
        update_data['completed'] = data['completed']

    result = tasks_collection.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': update_data}
    )

    if result.matched_count:
        return jsonify({'message': 'Task updated successfully'})
    else:
        return jsonify({'error': 'Task not found'}), 404


@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    result = tasks_collection.delete_one({'_id': ObjectId(task_id)})
    if result.deleted_count:
        return jsonify({'message': 'Task deleted successfully'})
    else:
        return jsonify({'error': 'Task not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)


