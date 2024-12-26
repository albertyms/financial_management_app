FROM python:3.12-slim

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
   gcc \
   libffi-dev \
   libssl-dev \
   && apt-get clean

# Set the working directory
WORKDIR /app

# Copy files into the app working directory
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#CMD ["python", "app.py"]

CMD ["flask", "run", "--host=0.0.0.0"]