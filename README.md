
# ⭐ RateHarvest: App Store Reviews Collector ⭐

  

A FastAPI-based service for collecting, analyzing, and storing App Store reviews with advanced sentiment analysis, metrics and insights.

  

## Prerequisites

  

- Python 3.8+

- MongoDB 6.0+

- Required Python packages (see requirements.txt)

  

## Installation

  

1. Clone the repository:

```bash
git  clone  <https://github.com/OksanaKunikevych/nebula.git>

cd  nebula/app
```

2. Create and activate a virtual environment (conda or venv)

  

3. Install dependencies:

```bash
pip  install  -r  requirements.txt
```

  

4. Set up MongoDB:

  

a. Install MongoDB:

```bash
# On macOS with Homebrew

brew tap mongodb/brew

brew install mongodb-community@6.0
```

  If you are using other OS follow the instructions here on the [official installation page](https://www.mongodb.com/docs/manual/installation/).

b. Start MongoDB service:

```bash
brew services start mongodb-community@6.0
```

  

c. Verify MongoDB installation:

```bash
# Connect to MongoDB shell
mongosh
# You should see a MongoDB shell prompt
# Exit the shell
> exit
```


Note: MongoDB runs as a background service. You only need to start it once, and it will automatically start on system boot. You don't need to keep a terminal window open for it.

  

## Project Structure

  

```

app-store-review-analysis/

├── app/

│ ├── api.py # API endpoints and routing

│ ├── database.py # MongoDB database operations

│ ├── main.py # FastAPI application setup

│ ├── metrics.py # Review metrics calculation

│ ├── models.py # Pydantic data models

│ ├── nlp_analysis.py # NLP and sentiment analysis

│ └── utils.py # Utility functions

├── requirements.txt # Python dependencies

└── README.md # Project documentation

```

  

## API Endpoints

 
| Endpoint                                      | Method | Description                                                                                                         | Parameters                        |
|-----------------------------------------------|--------|---------------------------------------------------------------------------------------------------------------------|-----------------------------------|
| `/api/v1/reviews/{app_id}/?limit=100`         | POST   | Collects new raw reviews, processes them, calculates metrics/insights, and stores all results in the database.     | `app_id` (required), `limit` (optional, default: 100) |
| `/api/v1/reviews/{app_id}/reviews/raw?limit=100` | GET    | Retrieves the raw reviews JSON data. This endpoint serves the unprocessed reviews and downloads the JSON file.     | `app_id` (required), `limit` (optional, default: 100) |
| `/api/v1/reviews/{app_id}/reviews/metrics`    | GET    | Retrieves aggregated metrics and insights, such as average rating and sentiment analysis, computed from reviews.   | `app_id` (required)             |


## Data Models

  

### Raw Review

```json
{
"app_id": "string",
"review_text": "string",
"review_title": "string",
"rating": "integer (1-5)",
"date_scraped": "datetime"
}
```

  

### Processed Review

```json
{
"app_id": "string",
"review_text": "string",
"review_title": "string",
"sentiment_score": "float (-1 to 1)",
"sentiment": "string (POSITIVE/NEGATIVE)",
"date_processed": "datetime"
}
```

  

### Review Metrics

```json
{
"last_updated": "datetime",
"average_rating": "float",
"rating_distribution": "object",
"total_reviews": "integer",
"review_length_stats": "object"
}
```
### Insights Metrics

```json
{
"last_updated": "datetime",
"overall_sentiment": "string",
"sentiment_score": "float",
"sentiment_distribution": "object",
"negative_keywords": "array",
"improvement_areas": "array",
"wordcloud_image": "string (base64)"
}
```

  

## How to use the API 

  
1. Start the API server:

```bash
uvicorn  app.main:app  --reload  --port  8001
```

2. Access the API documentation:

```
http://localhost:8001/docs
```

3. Example API calls:

a. Collect and process reviews:

```bash
curl -X POST "http://localhost:8001/api/v1/reviews/1459969523?limit=100"
```

  

b. Get raw reviews:

```bash
"http://localhost:8001/api/v1/reviews/1459969523/raw?limit=100"
```

c. Get metrics and insights:

```bash
"http://localhost:8001/api/v1/reviews/1459969523/metrics"
```

## Future plans and improvements

  
