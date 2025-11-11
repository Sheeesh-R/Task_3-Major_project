from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Sample tasks data (in a real app, this would be in a database)
tasks = [
    {
        "id": 1, 
        "title": "Complete project proposal", 
        "description": "Draft and finalize the project proposal document with the team.",
        "due_date": "2025-11-10", 
        "created_at": "2025-11-01",
        "priority": "high", 
        "completed": False,
        "subtasks": [
            {"id": 1, "title": "Outline key sections", "completed": True},
            {"id": 2, "title": "Write executive summary", "completed": False},
            {"id": 3, "title": "Add budget details", "completed": False}
        ],
        "labels": ["Work", "Urgent"]
    },
    {
        "id": 2, 
        "title": "Buy groceries", 
        "description": "Weekly grocery shopping for the household.",
        "due_date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 
        "created_at": (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
        "priority": "medium", 
        "completed": False,
        "subtasks": [],
        "labels": ["Personal", "Shopping"]
    },
    {
        "id": 3, 
        "title": "Call mom", 
        "description": "Weekly catch-up call with mom.",
        "due_date": "2025-11-09", 
        "created_at": "2025-11-05",
        "priority": "low", 
        "completed": False,
        "subtasks": [],
        "labels": ["Family", "Personal"]
    },
    {
        "id": 4, 
        "title": "Finish report", 
        "description": "Complete the quarterly financial report for the board meeting.",
        "due_date": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 
        "created_at": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        "priority": "high", 
        "completed": False,
        "subtasks": [
            {"id": 1, "title": "Gather financial data", "completed": True},
            {"id": 2, "title": "Create charts and graphs", "completed": True},
            {"id": 3, "title": "Write executive summary", "completed": False}
        ],
        "labels": ["Work", "Finance", "Urgent"]
    }
]

def get_overdue_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    return [task for task in tasks if not task['completed'] and task['due_date'] < today]

@app.route('/')
def index():
    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Filter out completed and overdue tasks from the main list
    active_tasks = [task for task in tasks if not task['completed'] and task['due_date'] >= today]
    overdue_tasks = get_overdue_tasks()
    
    # Sort tasks by due date
    active_tasks_sorted = sorted(active_tasks, key=lambda x: x['due_date'])
    overdue_tasks_sorted = sorted(overdue_tasks, key=lambda x: x['due_date'])
    
    return render_template('index.html', 
                         tasks=active_tasks_sorted, 
                         overdue_tasks=overdue_tasks_sorted,
                         today=today)

@app.route('/task/<int:task_id>')
def task_detail(task_id):
    # Find the task with the given ID
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    if task is None:
        # If no task is found with the given ID, redirect to the home page
        return redirect(url_for('index'))
    
    # Format the created_at date if it exists, otherwise use today's date
    if 'created_at' not in task:
        task['created_at'] = datetime.now().strftime('%Y-%m-%d')
    
    # Ensure subtasks and labels lists exist
    if 'subtasks' not in task:
        task['subtasks'] = []
    if 'labels' not in task:
        task['labels'] = []
    
    return render_template('task_detail.html', task=task)

@app.route('/task/<int:task_id>/subtask', methods=['POST'])
def add_subtask(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    
    if 'subtasks' not in task:
        task['subtasks'] = []
       
    # Get the new subtask title from the form data
    subtask_title = request.form.get('title')
    if not subtask_title:
        return jsonify({'error': 'Subtask title is required'}), 400
    
    # Generate a new subtask ID
    new_id = max([s['id'] for s in task['subtasks']], default=0) + 1
    
    # Add the new subtask
    task['subtasks'].append({
        'id': new_id,
        'title': subtask_title,
        'completed': False
    })
    
    return jsonify({
        'success': True,
        'subtask': {
            'id': new_id,
            'title': subtask_title,
            'completed': False
        }
    })

@app.route('/task/<int:task_id>/label', methods=['POST'])
def add_label(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    
    if 'labels' not in task:
        task['labels'] = []
    
    # Get the new label from the form data
    label = request.form.get('label')
    if not label:
        return jsonify({'error': 'Label is required'}), 400
    
    # Add the new label if it doesn't already exist
    if label not in task['labels']:
        task['labels'].append(label)
    
    return jsonify({
        'success': True,
        'label': label
    })

if __name__ == '__main__':
    app.run(debug=True)
