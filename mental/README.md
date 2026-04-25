# Mental Wellness Manager

A small Python application for managing health and mental wellness entries.

## Features

- Save daily wellness entries with mood, sleep, exercise, water, meditation, stress, and notes
- Persist data in `wellness_data.json`
- View a list of saved entries
- Show average summary statistics
- Display simple wellness trends over time

## Usage

Run the app from the `mental` folder:

```bash
python main.py add --mood 7 --sleep 7.5 --exercise 30 --water 8 --meditation 15 --stress 4 --notes "Feeling balanced"
python main.py list
python main.py summary
python main.py trends
```

## Requirements

- Python 3.9+
- Flask
- Gunicorn

## Local Web Service

Run the HTTP service locally for testing:

```bash
python app.py
```

Open `http://localhost:8080` to use the web UI.

The API endpoints are still available under `/api`:

- `GET /api/entries`
- `POST /api/entries`
- `GET /api/summary`
- `GET /api/trends`

## AlloyDB support

The app now supports the AlloyDB connector and direct PostgreSQL-style connection strings.

### Local fallback

- If neither AlloyDB connector settings nor `DATABASE_URL` is set, the app continues to use `wellness_data.json`.
- To use a local SQLite database for testing, set:

```bash
set DATABASE_URL=sqlite:///mental.db
python app.py
```

### AlloyDB connector setup

Use the AlloyDB connector by setting these environment variables:

```bash
set ALLOYDB_INSTANCE_CONNECTION_NAME=PROJECT:REGION:INSTANCE
set ALLOYDB_USER=DB_USER
set ALLOYDB_PASSWORD=DB_PASSWORD
set ALLOYDB_DATABASE=DATABASE_NAME
set ALLOYDB_IP_TYPE=PRIVATE
python app.py
```

The app will automatically use the AlloyDB connector when those values are present.

### Cloud Run deployment with AlloyDB connector

Deploy to Cloud Run with the AlloyDB environment variables:

```bash
gcloud run deploy mental-wellness \
  --image gcr.io/PROJECT_ID/mental-wellness \
  --platform managed \
  --region YOUR_REGION \
  --set-env-vars \
      ALLOYDB_INSTANCE_CONNECTION_NAME="PROJECT:REGION:INSTANCE",\
      ALLOYDB_USER="DB_USER",\
      ALLOYDB_PASSWORD="DB_PASSWORD",\
      ALLOYDB_DATABASE="DATABASE_NAME",\
      ALLOYDB_IP_TYPE="PRIVATE" \
  --allow-unauthenticated
```

### Direct `DATABASE_URL` option

If you prefer not to use the connector, you can still set:

```bash
set DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE_NAME
python app.py
```

> For AlloyDB on Cloud Run, use the AlloyDB connector when connecting via private IP and configure a Serverless VPC connector if necessary.

## Cloud Run Deployment

1. Build the container image:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/mental-wellness
```

2. Deploy to Cloud Run:

```bash
gcloud run deploy mental-wellness \
  --image gcr.io/PROJECT_ID/mental-wellness \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated
```

3. Use the deployed service endpoints:

- `GET /` - service info
- `GET /entries` - list entries
- `POST /entries` - add entry
- `GET /summary` - wellness summary
- `GET /trends` - wellness trends

Replace `PROJECT_ID` and `YOUR_REGION` with your Google Cloud project and region.
