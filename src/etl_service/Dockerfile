FROM python:3.11-slim

# Create directories
RUN mkdir -p /app/src/etl_service
RUN touch /app/src/__init__.py
WORKDIR /app


# Install Java and cron
RUN apt-get update && apt-get install -y openjdk-17-jdk cron

# Set Java environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

ENV PATH="$JAVA_HOME/bin:${PATH}"

# Install Python
RUN apt-get update && apt-get install -y python3

# Copy the ETL script and related files
COPY etl_script.py /app
COPY transform_utils.py /app/src/etl_service/
COPY load_utils.py /app/src/etl_service/
COPY redis_connector.py /app/src/etl_service/
COPY .env /app
COPY requirements.txt /app/src/etl_service/
COPY cronjob /app/src/etl_service/
COPY spark_session.py /app/src/etl_service/
COPY logging_config.py /app/src/etl_service/
COPY extract_utils.py /app/src/etl_service/

WORKDIR /app/src/etl_service

# Copy the Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the cronjob file and give it proper permissions
COPY cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cronjob
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start cron and tail the log file
CMD cron && tail -f /var/log/cron.log
