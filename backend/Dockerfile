# base image with Python and ffmpeg
FROM python:3.13-slim

# install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# set working directory
WORKDIR /app

# copying requirements first
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copying the rest of the backend code
COPY . /app

# exposing port
EXPOSE 8242

# starting uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8242"]
