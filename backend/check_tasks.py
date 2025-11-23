#!/usr/bin/env python
"""Quick script to check tasks in database"""
from app import app
from database import db
from models import Task

with app.app_context():
    print('All tasks by dataset:')
    movies = Task.query.filter_by(dataset_type='movies').all()
    books = Task.query.filter_by(dataset_type='books').all()
    print(f'Movies: {len(movies)} tasks')
    print(f'Books: {len(books)} tasks')
    
    print('\nBook tasks by interface:')
    for iface in ['faceted', 'llm_assist', 'llm_only']:
        count = len([t for t in books if t.interface_type == iface])
        print(f'  {iface}: {count} tasks')
        if count > 0:
            for task in [t for t in books if t.interface_type == iface]:
                print(f'    - {task.task_id}: {task.description[:60]}...')

