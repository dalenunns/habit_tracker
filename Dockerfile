FROM python:3.11-slim-bookworm

# Install requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Home Assistant Add-ons store persistent data in /data
# We will point our Flask app there
ENV SQLALCHEMY_DATABASE_URI="sqlite:////data/habits.db"

# Make run script executable
RUN chmod a+x /app/run.sh

CMD [ "/app/run.sh" ]