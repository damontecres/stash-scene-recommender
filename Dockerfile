# syntax=docker/dockerfile:1
FROM --platform=$BUILDPLATFORM python:3.13-slim

WORKDIR /app

COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY app.py /app
COPY sceneRecommender /app/sceneRecommender

ENTRYPOINT ["python3"]
CMD ["app.py"]
