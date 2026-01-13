# Habit Tracker HomeAssistant Add-on

A simple web-based habit tracking application designed to run as a HomeAssistant add-on. Track your daily habits, log activities with timestamps and comments, and view progress reports.

## Features

- **Habit Management**: Create and manage custom habits with icons and default intervals
- **Activity Logging**: Log habit completions with optional comments and custom time intervals
- **Progress Reports**: View statistics and timelines of your habit tracking
- **Maintenance Mode**: Edit or delete habits and logs
- **Persistent Storage**: SQLite database stored in HomeAssistant's persistent data directory
- **Ingress Integration**: Seamlessly integrates with HomeAssistant's sidebar via ingress

## What It Does

This add-on provides a clean web interface for habit tracking. Users can:

1. Define habits they want to track (e.g., "Exercise", "Read", "Meditate")
2. Click on habit cards to log completions
3. Add comments and specify time spent on activities
4. View reports showing habit frequency and time breakdowns
5. Manage habits and logs through a maintenance interface

The app stores all data in a SQLite database at `/data/habits.db` within the HomeAssistant environment, ensuring data persistence across restarts.

## HomeAssistant Add-on Integration

This project is specifically designed as a HomeAssistant add-on:

- **Ingress Support**: Uses HomeAssistant's ingress system for secure access through the HA sidebar
- **Persistent Data**: Stores data in HA's `/data` directory for persistence
- **Containerized**: Runs in a Docker container with Python 3.11
- **Multi-Architecture**: Supports aarch64, amd64, and armv7 architectures

### Installation as Add-on

1. Copy the `habit_tracker` folder to your HomeAssistant `addons` directory
2. Restart HomeAssistant
3. Go to Settings → Add-ons → Habit Tracker → Install
4. Start the add-on
5. Access it through the sidebar under "Habit Tracker"

### Configuration

The add-on requires no configuration options. It automatically:
- Sets up the database at `/data/habits.db`
- Configures ingress for web access
- Runs on port 5000 internally

## Local Development/Running

If you want to run this outside of HomeAssistant:

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running Locally

1. Set the database path (optional, defaults to `habits.db` in current directory):
   ```bash
   export SQLALCHEMY_DATABASE_URI="sqlite:///habits.db"
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open http://localhost:5000 in your browser

### Docker

Build and run with Docker:

```bash
docker build -t habit-tracker .
docker run -p 5000:5000 -v $(pwd)/data:/data habit-tracker
```

## API Endpoints

The app provides a REST API for external integrations:

- `GET /api/habits` - List all habits
- `POST /api/habits` - Create a new habit
- `POST /api/log` - Log a habit completion
- `POST /api/log/manual` - Log with custom timestamp
- `DELETE /api/log/<id>` - Delete a log entry
- `DELETE /api/habit/<id>` - Delete a habit
- `GET /api/stats` - Get statistics data

## Architecture

- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for simplicity and persistence
- **Frontend**: HTML templates with vanilla JavaScript
- **Styling**: Simple CSS for responsive design
- **Deployment**: Docker container optimized for HomeAssistant add-ons

## Contributing

Feel free to submit issues and pull requests for improvements or bug fixes.