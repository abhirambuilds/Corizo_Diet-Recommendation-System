# Personalized Diet Recommendation System

A machine learning-powered web application that provides personalized diet recommendations based on user health profiles using K-Means clustering.

## 📋 Project Overview

This application uses K-Means clustering (k=6) to analyze user health data and recommend appropriate foods. The system takes into account factors such as age, BMI, chronic diseases, blood pressure, blood sugar levels, activity levels, and lifestyle habits to create personalized diet profiles.

### Features

- **Intelligent Clustering**: Uses K-Means clustering to categorize users into 6 distinct health profiles
- **Personalized Recommendations**: Provides top 10 food recommendations based on nutritional scoring
- **RESTful API**: Clean Flask backend with comprehensive validation
- **Modern Frontend**: Responsive web interface with client-side validation
- **Real-time Scoring**: Ranks foods using a smart algorithm: `(Protein×2) - (Fat×1.5) - (Calories/50)`

## 🖼️ Screenshots

*Screenshots will be added here*

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Running the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask server:
   ```bash
   python app.py
   ```

   The API will be available at `http://127.0.0.1:5000`

**Windows users**: You can use the helper script:
```bash
cd backend
run.bat
```

### Running the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the HTTP server:
   ```bash
   python -m http.server 5500
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5500/index.html
   ```

**Windows users**: You can use the helper script:
```bash
cd frontend
serve.bat
```

## 📡 API Endpoints

### Base URL
```
http://127.0.0.1:5000
```

### Endpoints

#### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "running"
}
```

#### `GET /api/health`
API health check.

**Response:**
```json
{
  "ok": true
}
```

#### `GET /api/schema`
Returns the expected input schema including required keys and allowed categorical values.

**Response:**
```json
{
  "required_keys": [
    "Age", "BMI", "Chronic_Disease", "Blood_Pressure_Systolic",
    "Blood_Sugar_Level", "Daily_Steps", "Exercise_Frequency",
    "Alcohol_Consumption", "Smoking_Habit", "Dietary_Habits"
  ],
  "allowed_values": {
    "Chronic_Disease": ["None", "Diabetes", "Heart Disease", "Hypertension", "Obesity"],
    "Alcohol_Consumption": ["No", "Yes"],
    "Smoking_Habit": ["No", "Yes"],
    "Dietary_Habits": ["Regular", "Vegetarian", "Vegan", "Keto"]
  },
  "field_types": {
    "Age": "number (integer)",
    "BMI": "number (float)",
    "Chronic_Disease": "string (categorical)",
    "Blood_Pressure_Systolic": "number (integer)",
    "Blood_Sugar_Level": "number (integer)",
    "Daily_Steps": "number (integer)",
    "Exercise_Frequency": "number (integer)",
    "Alcohol_Consumption": "string (categorical)",
    "Smoking_Habit": "string (categorical)",
    "Dietary_Habits": "string (categorical)"
  }
}
```

#### `GET /api/test` or `POST /api/test`
Returns a mock response matching the real recommendation schema. Useful for testing the frontend.

**Response:**
```json
{
  "profile_name": "Cluster 2",
  "recommendation_type": "Low-Fat Foods",
  "recommended_foods": [
    {
      "Food": "Broccoli",
      "Category": "Vegetables",
      "Protein": 2.8,
      "Fat": 0.4,
      "Carbs": 6.6,
      "Calories": 34.0
    },
    ...
  ]
}
```

#### `POST /api/recommend`
Generate personalized diet recommendations based on user data.

**Request Body:**
```json
{
  "Age": 25,
  "BMI": 23.5,
  "Chronic_Disease": "None",
  "Blood_Pressure_Systolic": 120,
  "Blood_Sugar_Level": 90,
  "Daily_Steps": 7000,
  "Exercise_Frequency": 3,
  "Alcohol_Consumption": "No",
  "Smoking_Habit": "No",
  "Dietary_Habits": "Regular"
}
```

**Validation Rules:**
- **Age**: 1-100 (integer)
- **BMI**: 10-60 (float)
- **Blood Pressure**: 80-200 (integer)
- **Blood Sugar**: 50-400 (integer)
- **Daily Steps**: 0-30000 (integer)
- **Exercise Frequency**: 0-7 (integer per week)
- **Categorical fields**: Must match allowed values exactly

**Response (Success - 200):**
```json
{
  "profile_name": "Prediabetic, Active Profile",
  "recommendation_type": "Low-Carb Foods",
  "recommended_foods": [
    {
      "Food": "Turkey",
      "Category": "Meat, Poultry",
      "Protein": 27.0,
      "Fat": 15.0,
      "Carbs": 0.0,
      "Calories": 265.0
    },
    ...
  ]
}
```

**Response (Error - 400):**
```json
{
  "error": "Invalid value for 'Dietary_Habits': 'Low-Carb'",
  "allowed": {
    "Dietary_Habits": ["Regular", "Vegetarian", "Vegan", "Keto"]
  }
}
```

## 🎯 Cluster Profiles

The system uses 6 distinct health profiles:

1. **Cluster 0**: Prediabetic, Active Profile → Low-Carb Foods
2. **Cluster 1**: Older, Active Diabetic Profile → Low-Carb Foods
3. **Cluster 2**: Active Diabetic with High Blood Pressure → Low-Fat Foods
4. **Cluster 3**: Low-Activity Diabetic with Very High Blood Sugar → Low-Carb Foods
5. **Cluster 4**: Active Walker with High Blood Pressure → Low-Fat Foods
6. **Cluster 5**: High BMI (Obese) with Diabetes → Balanced (Low-Calorie) Foods

## 🔧 Tech Stack

### Backend
- **Flask**: Web framework
- **scikit-learn**: Machine learning (K-Means clustering)
- **pandas**: Data manipulation
- **joblib**: Model serialization
- **flask-cors**: Cross-origin resource sharing

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling (custom CSS with modern design)
- **JavaScript (Vanilla)**: Client-side logic and API integration

### Machine Learning
- **K-Means Clustering**: Unsupervised learning for user segmentation
- **Feature Engineering**: StandardScaler for numerical features, OneHotEncoder for categorical features

## 📁 Project Structure

```
diet-app/
├── backend/
│   ├── app.py                          # Flask API server
│   ├── requirements.txt                 # Python dependencies
│   ├── run.bat                         # Windows helper script
│   ├── kmeans_model.joblib             # Trained K-Means model
│   ├── preprocessor.joblib             # Data preprocessor
│   ├── preprocessor_and_features.joblib # Preprocessor with features
│   └── nutrients_csvfile.csv           # Food database
├── frontend/
│   ├── index.html                      # Main HTML file
│   ├── css/
│   │   └── styles.css                  # Styling
│   ├── js/
│   │   └── app.js                      # Frontend logic
│   └── serve.bat                       # Windows helper script
├── _archive/                           # Archived files (not needed to run)
│   ├── *.ipynb                         # Training & EDA notebooks
│   ├── eda_plots/                      # Exploratory data analysis plots
│   ├── plots/                          # Model training visualizations
│   ├── data/                           # Processed data files
│   └── Personalized_Diet_Recommendations.csv  # Training dataset
├── README.md                           # This file
├── TEST_NOTES.md                       # Test documentation
└── .gitignore                          # Git ignore rules
```

### Project Layout

- **`backend/`** - Flask API server with model files and food database
  - Contains all necessary files to run the API (models, data, code)
  - Run with: `python app.py` or `run.bat` (Windows)

- **`frontend/`** - Web interface (HTML, CSS, JavaScript)
  - Standalone frontend that communicates with the backend API
  - Serve with: `python -m http.server 5500` or `serve.bat` (Windows)

- **`_archive/`** - Historical files (not needed to run the app)
  - Training notebooks (`.ipynb` files)
  - EDA plots and visualizations
  - Intermediate data files
  - These are kept for reference but not required for deployment

## 🔍 How It Works

1. **User Input**: User fills out health information form
2. **Validation**: Client-side and server-side validation ensures data quality
3. **Preprocessing**: Data is normalized and encoded using the trained preprocessor
4. **Clustering**: K-Means model predicts which cluster the user belongs to
5. **Food Selection**: 
   - If Cluster column exists in dataset, filter by cluster
   - Calculate nutritional score: `(Protein×2) - (Fat×1.5) - (Calories/50)`
   - Sort by score and return top 10 foods
6. **Response**: Returns personalized recommendations with profile name and recommendation type

## 📝 Notes

- The backend logs all requests and predicted clusters at INFO level
- CORS is restricted to `http://127.0.0.1:5500` and `http://localhost:5500`
- All numeric values are validated and NaN values are filled with 0
- The scoring algorithm prioritizes high protein, low fat, and low calories

## 📄 License

This project is available for educational and personal use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

*For detailed API documentation, visit `/api/schema` endpoint when the server is running.*

