import os
from flask import Flask, render_template, request, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Essential for Ingress: Tells Flask to trust the headers sent by Home Assistant
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Persistent storage for HA
db_path = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////data/habits.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False  # Ensures JSON stays as Unicode
app.config['SQLALCHEMY_NATIVE_UNICODE'] = True

db = SQLAlchemy(app)

@app.after_request
def add_header(response):
    # This forces the browser to interpret the response as UTF-8
    if response.mimetype == 'text/html':
        response.charset = 'utf-8'
    return response

# --- Database Models ---
class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    default_interval = db.Column(db.Integer, default=0)

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.String(200))
    interval = db.Column(db.Integer)
    habit = db.relationship('Habit', backref=db.backref('logs', lazy=True))

with app.app_context():
    db.create_all()

# --- HA Ingress Context Processor ---
# This makes 'root_path' available in every single HTML template automatically
@app.context_processor
def inject_ingress_path():
    # HA sends the path in 'X-Ingress-Path' header
    return dict(root_path=request.headers.get('X-Ingress-Path', ''))

# --- Web Routes ---
@app.route('/')
def index():
    habits = Habit.query.all()
    return render_template('index.html', habits=habits)

@app.route('/report')
def report():
    logs = HabitLog.query.order_by(HabitLog.timestamp.desc()).all()
    return render_template('report.html', logs=logs)

@app.route('/maintenance')
def maintenance():
    habits = Habit.query.all()
    logs = HabitLog.query.order_by(HabitLog.timestamp.desc()).limit(100).all()
    return render_template('maintenance.html', habits=habits, logs=logs)

# --- API Routes ---
@app.route('/api/habits', methods=['GET', 'POST'])
def api_habits():
    if request.method == 'POST':
        data = request.json
        new_habit = Habit(title=data.get('title'), icon=data.get('icon', '📝'), default_interval=int(data.get('default_interval', 0)))
        db.session.add(new_habit)
        db.session.commit()
        return jsonify({'success': True}), 201
    return jsonify([{'id': h.id, 'title': h.title, 'icon': h.icon} for h in Habit.query.all()])

@app.route('/api/log', methods=['POST'])
def api_log_habit():
    data = request.json
    habit = db.get_or_404(Habit, data['habit_id'])
    final_interval = int(data.get('interval')) if data.get('interval') else habit.default_interval
    new_log = HabitLog(habit_id=habit.id, comment=data.get('comment', ''), interval=final_interval)
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'success': True}), 201

@app.route('/api/log/manual', methods=['POST'])
def manual_log():
    data = request.json
    new_log = HabitLog(habit_id=data['habit_id'], comment=data.get('comment', ''), timestamp=datetime.strptime(data['timestamp'], '%Y-%m-%dT%H:%M'), interval=int(data.get('interval', 0)))
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'success': True}), 201

@app.route('/api/log/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    log = db.get_or_404(HabitLog, log_id); db.session.delete(log); db.session.commit()
    return jsonify({'success': True})

@app.route('/api/habit/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    habit = db.get_or_404(Habit, habit_id)
    HabitLog.query.filter_by(habit_id=habit_id).delete()
    db.session.delete(habit); db.session.commit()
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    count_query = db.session.query(Habit.title, func.count(HabitLog.id)).outerjoin(HabitLog).group_by(Habit.id).all()
    time_query = db.session.query(Habit.title, func.sum(HabitLog.interval)).outerjoin(HabitLog).group_by(Habit.id).all()
    daily_logs = db.session.query(func.date(HabitLog.timestamp), func.count(HabitLog.id)).group_by(func.date(HabitLog.timestamp)).all()
    return jsonify({
        'breakdown': {'labels': [h[0] for h in count_query], 'counts': [h[1] for h in count_query], 'minutes': [h[1] or 0 for h in time_query]},
        'timeline': {'labels': [d[0] for d in daily_logs if d[0]], 'data': [d[1] for d in daily_logs if d[0]]}
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)