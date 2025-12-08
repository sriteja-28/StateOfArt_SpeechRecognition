# base image with Python and ffmpeg
FROM python:3.13-slim

# install ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# set working directory
WORKDIR /app

# copy code
COPY backend/ /app

# install dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# expose port
EXPOSE 8242

# start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8242"]
