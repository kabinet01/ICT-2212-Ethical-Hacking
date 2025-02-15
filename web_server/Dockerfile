    FROM python:3.9-slim

    RUN apt-get update && apt-get install -y sqlite3 cron nano zip lftp && rm -rf /var/lib/apt/lists/*

    WORKDIR /app
    COPY ./service /app

    RUN mv clear_facts.sh /opt/clear_facts.sh
    RUN mv apikey.txt /apikey.txt
    RUN chmod 644 /apikey.txt && chmod 777 /opt/clear_facts.sh
    RUN pip install --no-cache-dir -r requirements.txt

    RUN mv crontab /etc/crontab
    RUN chmod 0644 /etc/crontab

    RUN adduser --disabled-password --gecos '' flask_app

    RUN chown -R flask_app:flask_app /app

    USER flask_app

    RUN mkdir -p /tmp/fact_app/uploads /tmp/fact_app/downloads

    
    # Make port 80 available to the world outside this container
    EXPOSE 80

    # Create the database and populate it with initial data
    RUN python create_db.py

    # Switch back to root to start cron and then switch to flask_app to run the app
    USER root
    CMD cron && su flask_app -c "gunicorn --bind 0.0.0.0:80 app:app"