# ⭐ RateHarvest: App Store Reviews Collector ⭐

A FastAPI-based service for collecting, analyzing, and storing App Store reviews with advanced sentiment analysis, metrics, and insights.

---

## Prerequisites

- **Python** 3.8+
- **MongoDB** 6.0+
- **Required Python packages** (see `requirements.txt`)

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/OksanaKunikevych/nebula.git
cd nebula
```

### 2️⃣ Create and activate a virtual environment (conda or venv)

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up MongoDB

#### a. Install MongoDB

```bash
# On macOS with Homebrew
brew tap mongodb/brew
brew install mongodb-community@6.0
```

For other OS, follow the instructions on the [official installation page](https://www.mongodb.com/docs/manual/installation/).

#### b. Start MongoDB service

```bash
brew services start mongodb-community@6.0
```

#### c. Verify MongoDB installation

```bash
# Connect to MongoDB shell
mongosh
# You should see a MongoDB shell prompt
# Exit the shell
> exit
```

💡 **Note:** MongoDB runs as a background service. You only need to start it once, and it will automatically start on system boot.

---

## 📂 Project Structure

```
app-store-review-analysis/
├── app/
│   ├── api.py            # API endpoints and routing
│   ├── database.py       # MongoDB database operations
│   ├── main.py           # FastAPI application setup
│   ├── metrics.py        # Review metrics calculation
│   ├── models.py         # Pydantic data models
│   ├── nlp_analysis.py   # NLP and sentiment analysis
│   └── utils.py          # Utility functions
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 📡 API Endpoints

| Endpoint                                      | Method | Description                                                                                                         | Parameters                                      |
|-----------------------------------------------|--------|---------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| `/api/v1/reviews/{app_id}/?limit=100`         | POST   | Collects new raw reviews, processes them, calculates metrics/insights, and stores all results in the database.     | `app_id` (required), `limit` (optional, default: 100) |
| `/api/v1/reviews/{app_id}/reviews/raw?limit=100` | GET    | Retrieves the raw reviews JSON data. This endpoint serves the unprocessed reviews and downloads the JSON file.     | `app_id` (required), `limit` (optional, default: 100) |
| `/api/v1/reviews/{app_id}/reviews/metrics`    | GET    | Retrieves aggregated metrics and insights, such as average rating and sentiment analysis, computed from reviews.   | `app_id` (required)                                 |

---

## Endpoints workflow
<img width="783" alt="Screenshot 2025-03-19 at 5 54 12 PM" src="https://github.com/user-attachments/assets/acf4cb60-ed4a-433c-b94b-a3ead2efeb6b" />

---

## 🔧 How to Use the API

### 1️⃣ Start the API server

```bash
uvicorn app.main:app --reload --port 8001
```

### 2️⃣ Access the API documentation

```
http://localhost:8001/docs
```

### 3️⃣ Example API calls

💡 Note: To find an app id in App Store:
1. Search for the app in the Apple App Store.
2. The App ID is the numeric value in the URL, right after /id:
https://apps.apple.com/us/app/sleep-cycle-tracker-sounds/id**320606217**


#### a. Collect and process reviews

```bash
curl -X POST "http://localhost:8001/api/v1/reviews/1459969523?limit=100"
```

#### b. Get raw reviews

```bash
http://localhost:8001/api/v1/reviews/1459969523/raw?limit=100
```

#### c. Get metrics and insights

```bash
http://localhost:8001/api/v1/reviews/1459969523/metrics
```

## Using the Basic UI

The project includes a simple HTML interface (`index.html`) for basic interaction with the API:

1. Open the index.html file in your web browser


2. Features:
   - Real-time review collection and analysis
   - Visual representation of review metrics and insights

Note: This is a very basic v0 UI implementation.

## 📝 Data Models

### 📌 Raw Review

```json
{
  "app_id": "string",
  "review_text": "string",
  "review_title": "string",
  "rating": "integer (1-5)",
  "date_scraped": "datetime"
}
```

### 📌 Processed Review

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

### 📌 Review Metrics

```json
{
  "last_updated": "datetime",
  "average_rating": "float",
  "rating_distribution": "object",
  "total_reviews": "integer",
  "review_length_stats": "object"
}
```

### 📌 Insights Metrics

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

---

## Future plans and improvements
- More insights ideas: 
  - correlations between review_length_stats and rating, better keyword extraction
  - detect change of sentiment
  - collect ideas for feature requests (topic modeling)
  - detect mentions of competitors (NER)

- technical improvements:
  - Retrieve app id from app name (currently restricted by third-party scraper library)
  - Raw download endpoint: enhance to download either raw or processed with ?type=“raw/processed”
  - Add test coverage
  
More info: [App Store Reviews Collector Notion](https://sky-surf-0ef.notion.site/App-Store-Reviews-Collector-1bb97b8d71b2809db786f8ccb62f0743)