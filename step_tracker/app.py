from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///steps.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class StepRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steps = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(10), nullable=False, unique=True)  # Формат YYYY-MM-DD

    def __repr__(self):
        return f'<StepRecord {self.date}: {self.steps} steps>'


@app.before_request
def initialize_database():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True


@app.route('/')
def index():
    records = StepRecord.query.order_by(StepRecord.date.desc()).all()
    total_steps = sum(record.steps for record in records)
    return render_template('index.html', records=records, total_steps=total_steps)


@app.route('/add', methods=['POST'])
def add_record():
    steps = request.form.get('steps', type=int)
    date = request.form.get('date')

    if not steps or not date:
        return redirect(url_for('index'))

    existing_record = StepRecord.query.filter_by(date=date).first()
    if existing_record:
        existing_record.steps = steps
    else:
        new_record = StepRecord(steps=steps, date=date)
        db.session.add(new_record)

    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_record(id):
    record = StepRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)