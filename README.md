# Stash Scene Recommender

> [!WARNING]
> This is very experimental and a work in progress!

This is a content-based scene recommender for Stash. It uses TF-IDF vectorization and cosine similarity to recommend scenes based on tags, performers, studios, and directors.

## Usage

Can either build/run the docker image or run directly with Python (`python app.py`).

Once running, get list of recommendations with the API at `http://localhost:8000/recommend/<scene_id>`

## Configuration

Set environment variables to connect to your Stash instance:
- `STASH_SCHEME` - `http` or `https`, default `http`
- `STASH_HOST` - hostname or IP address of your Stash instance, default `localhost`
- `STASH_PORT` - port number of your Stash instance, default `9999`
- `STASH_API_KEY` - optional, your Stash API key

Additionally, you can set:
- `IGNORED_TAGS` - comma-separated list of tag IDs to ignore in recommendations

## Docker
Build the image:
```bash
docker build -t stash-scene-recommender .
```
Run the container:
```bash
docker run -d -p 8000:8000 \
  -e STASH_HOST=your-stash-host \
  -e STASH_API_KEY=your-api-key \
  stash-scene-recommender
```

## Plugin

There's a rough Stash plugin which allows for running the recommender as a plugin task.

Due to the python dependencies, it can be complicated to set up, especially when Stash is running in alpine Docker.
