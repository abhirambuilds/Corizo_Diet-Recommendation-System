"""
Diet Recommendation API - Flask Backend

Cluster-to-Profile Mapping (based on K-Means clustering with k=6):
This mapping is extracted from Testing.ipynb and Model_Training.ipynb analysis.

Cluster 0: "Prediabetic, Active Profile"
  - Profile: Users with moderate activity, prediabetic conditions
  - Recommendation Type: "Low-Carb Foods"
  - Sorting: By Carbs (ascending)

Cluster 1: "Older, Active Diabetic Profile"
  - Profile: Older users with diabetes but maintaining active lifestyle
  - Recommendation Type: "Low-Carb Foods"
  - Sorting: By Carbs (ascending)

Cluster 2: "Active Diabetic with High Blood Pressure"
  - Profile: Diabetic users with high blood pressure, active lifestyle
  - Recommendation Type: "Low-Fat Foods"
  - Sorting: By Fat (ascending)

Cluster 3: "Low-Activity Diabetic with Very High Blood Sugar"
  - Profile: Diabetic users with high blood sugar, low activity levels
  - Recommendation Type: "Low-Carb Foods"
  - Sorting: By Carbs (ascending)

Cluster 4: "Active Walker with High Blood Pressure"
  - Profile: Active users with high blood pressure concerns
  - Recommendation Type: "Low-Fat Foods"
  - Sorting: By Fat (ascending)

Cluster 5: "High BMI (Obese) with Diabetes"
  - Profile: Obese diabetic users requiring calorie management
  - Recommendation Type: "Balanced (Low-Calorie) Foods"
  - Sorting: By Calories (ascending)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import warnings
import logging

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Restrict CORS to specific origins (frontend server)
CORS(app, origins=['http://127.0.0.1:5500', 'http://localhost:5500'])

# Expected JSON keys (exact match required)
REQUIRED_KEYS = [
    "Age", "BMI", "Chronic_Disease", "Blood_Pressure_Systolic",
    "Blood_Sugar_Level", "Daily_Steps", "Exercise_Frequency",
    "Alcohol_Consumption", "Smoking_Habit", "Dietary_Habits"
]

# Allowed categorical values
ALLOWED_VALUES = {
    "Chronic_Disease": ["None", "Diabetes", "Heart Disease", "Hypertension", "Obesity"],
    "Alcohol_Consumption": ["No", "Yes"],
    "Smoking_Habit": ["No", "Yes"],
    "Dietary_Habits": ["Regular", "Vegetarian", "Vegan", "Keto"]
}

# Cluster-to-Profile Mapping (extracted from Testing.ipynb)
# Maps cluster number to descriptive profile name
CLUSTER_PROFILE = {
    0: "Prediabetic, Active Profile",
    1: "Older, Active Diabetic Profile",
    2: "Active Diabetic with High Blood Pressure",
    3: "Low-Activity Diabetic with Very High Blood Sugar",
    4: "Active Walker with High Blood Pressure",
    5: "High BMI (Obese) with Diabetes"
}

# Cluster-to-Recommendation Type Mapping
# Maps cluster number to recommendation type
CLUSTER_RECOMMENDATION_TYPE = {
    0: "Low-Carb Foods",
    1: "Low-Carb Foods",
    2: "Low-Fat Foods",
    3: "Low-Carb Foods",
    4: "Low-Fat Foods",
    5: "Balanced (Low-Calorie) Foods"
}

# Global variables to store loaded models and data
model = None
preprocessor = None
features_list = None
food_df = None

def load_models_and_data():
    """Load the preprocessor, model, and food data at startup."""
    global model, preprocessor, features_list, food_df
    
    try:
        # Load preprocessor and features list
        # Try loading preprocessor_and_features.joblib first (preferred)
        if os.path.exists('preprocessor_and_features.joblib'):
            model_payload = joblib.load('preprocessor_and_features.joblib')
            preprocessor = model_payload['preprocessor']
            features_list = model_payload['feature_list']
        # Fallback to separate preprocessor.joblib if needed
        elif os.path.exists('preprocessor.joblib'):
            preprocessor = joblib.load('preprocessor.joblib')
            # Define features list manually if not in preprocessor file
            features_list = [
                'Age', 'BMI', 'Chronic_Disease', 'Blood_Pressure_Systolic', 
                'Blood_Sugar_Level', 'Daily_Steps', 'Exercise_Frequency', 
                'Alcohol_Consumption', 'Smoking_Habit', 'Dietary_Habits'
            ]
        else:
            raise FileNotFoundError("Neither preprocessor_and_features.joblib nor preprocessor.joblib found")
        
        # Load the K-Means model
        model = joblib.load('kmeans_model.joblib')
        
        # Load the food database
        food_df = pd.read_csv('nutrients_csvfile.csv')
        
        # Clean numeric columns (handle 't' for trace values and commas)
        numeric_cols = ['Grams', 'Calories', 'Protein', 'Fat', 'Sat.Fat', 'Fiber', 'Carbs']
        for col in numeric_cols:
            if col in food_df.columns and food_df[col].dtype == 'object':
                food_df[col] = food_df[col].astype(str).str.replace('t', '0', regex=False)
                food_df[col] = food_df[col].astype(str).str.replace(',', '', regex=False)
                food_df[col] = pd.to_numeric(food_df[col], errors='coerce')
        
        # Fill NaN values with 0
        food_df[numeric_cols] = food_df[numeric_cols].fillna(0)
        
        print("Models and data loaded successfully!")
        return True
        
    except FileNotFoundError as e:
        print(f"ERROR: Could not load models or data. File not found: {e}")
        return False
    except Exception as e:
        print(f"An error occurred during loading: {e}")
        return False

def get_cluster_recommendations(user_cluster):
    """
    Get food recommendations based on the predicted cluster.
    Uses CLUSTER_PROFILE and CLUSTER_RECOMMENDATION_TYPE dictionaries.
    
    Selection logic:
    1. Filter by Cluster column if it exists in the dataset
    2. If Cluster column doesn't exist, use entire dataset
    3. Calculate score: (Protein*2) - (Fat*1.5) - (Calories/50)
       Higher score = better (higher protein, lower fat, lower calories)
    4. Rank by score and return top 10
    
    Returns profile_name, recommendation_type, and recommended_foods DataFrame.
    """
    # Get profile name from mapping, fallback to generic if cluster not found
    profile_name = CLUSTER_PROFILE.get(user_cluster, f"Cluster {user_cluster}")
    
    # Get recommendation type from mapping, fallback to default
    recommendation_type = CLUSTER_RECOMMENDATION_TYPE.get(
        user_cluster, 
        "Balanced (Low-Calorie) Foods"
    )
    
    # Start with the full dataset
    working_df = food_df.copy()
    
    # Filter by Cluster if column exists
    if 'Cluster' in working_df.columns:
        # Ensure Cluster column is numeric for comparison
        working_df['Cluster'] = pd.to_numeric(working_df['Cluster'], errors='coerce')
        # Filter by predicted cluster
        working_df = working_df[working_df['Cluster'] == user_cluster]
        
        # If no foods match the cluster, fall back to entire dataset
        if len(working_df) == 0:
            print(f"Warning: No foods found for Cluster {user_cluster}, using entire dataset")
            working_df = food_df.copy()
    
    # Ensure required numeric columns exist and are numeric
    numeric_cols = ['Protein', 'Fat', 'Calories']
    for col in numeric_cols:
        if col not in working_df.columns:
            working_df[col] = 0
        else:
            # Convert to numeric, handling any string values
            working_df[col] = pd.to_numeric(working_df[col], errors='coerce')
    
    # Fill NaN values with 0 for numeric columns
    working_df[numeric_cols] = working_df[numeric_cols].fillna(0)
    
    # Calculate score: (Protein*2) - (Fat*1.5) - (Calories/50)
    # Higher score is better (more protein, less fat, fewer calories)
    working_df['score'] = (
        (working_df['Protein'] * 2) - 
        (working_df['Fat'] * 1.5) - 
        (working_df['Calories'] / 50)
    )
    
    # Sort by score descending (higher score = better) and get top 10
    recommended_foods = working_df.sort_values(by='score', ascending=False).head(10)
    
    # Select only the required fields
    required_fields = ['Food', 'Category', 'Protein', 'Fat', 'Carbs', 'Calories']
    
    # Ensure all required fields exist
    for field in required_fields:
        if field not in recommended_foods.columns:
            if field in ['Protein', 'Fat', 'Carbs', 'Calories']:
                recommended_foods[field] = 0
            else:
                recommended_foods[field] = ''
    
    # Ensure Carbs is numeric and filled
    if 'Carbs' in recommended_foods.columns:
        recommended_foods['Carbs'] = pd.to_numeric(recommended_foods['Carbs'], errors='coerce').fillna(0)
    
    # Select and return only required fields
    recommended_foods = recommended_foods[required_fields].copy()
    
    # Final cleanup: ensure all numeric fields are properly formatted
    numeric_fields = ['Protein', 'Fat', 'Carbs', 'Calories']
    for field in numeric_fields:
        if field in recommended_foods.columns:
            recommended_foods[field] = pd.to_numeric(recommended_foods[field], errors='coerce').fillna(0)
    
    return profile_name, recommendation_type, recommended_foods

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "running"})

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint."""
    return jsonify({"ok": True})

@app.route('/api/test', methods=['GET', 'POST'])
def api_test():
    """Test endpoint returning mock response matching real schema."""
    # Mock response matching the real recommendation schema
    mock_response = {
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
            {
                "Food": "Spinach",
                "Category": "Vegetables",
                "Protein": 2.9,
                "Fat": 0.4,
                "Carbs": 3.6,
                "Calories": 23.0
            },
            {
                "Food": "Cucumber",
                "Category": "Vegetables",
                "Protein": 0.7,
                "Fat": 0.1,
                "Carbs": 3.6,
                "Calories": 16.0
            },
            {
                "Food": "Lettuce",
                "Category": "Vegetables",
                "Protein": 1.4,
                "Fat": 0.2,
                "Carbs": 2.9,
                "Calories": 15.0
            },
            {
                "Food": "Celery",
                "Category": "Vegetables",
                "Protein": 0.7,
                "Fat": 0.2,
                "Carbs": 3.0,
                "Calories": 16.0
            },
            {
                "Food": "Tomato",
                "Category": "Vegetables",
                "Protein": 0.9,
                "Fat": 0.2,
                "Carbs": 3.9,
                "Calories": 18.0
            },
            {
                "Food": "Bell Pepper",
                "Category": "Vegetables",
                "Protein": 1.0,
                "Fat": 0.3,
                "Carbs": 4.6,
                "Calories": 20.0
            },
            {
                "Food": "Zucchini",
                "Category": "Vegetables",
                "Protein": 1.2,
                "Fat": 0.2,
                "Carbs": 3.4,
                "Calories": 17.0
            },
            {
                "Food": "Cauliflower",
                "Category": "Vegetables",
                "Protein": 1.9,
                "Fat": 0.3,
                "Carbs": 5.0,
                "Calories": 25.0
            },
            {
                "Food": "Asparagus",
                "Category": "Vegetables",
                "Protein": 2.2,
                "Fat": 0.2,
                "Carbs": 3.9,
                "Calories": 20.0
            }
        ]
    }
    return jsonify(mock_response), 200

@app.route('/api/schema', methods=['GET'])
def api_schema():
    """Return the expected input schema including required keys and allowed categorical values."""
    schema = {
        "required_keys": REQUIRED_KEYS,
        "allowed_values": ALLOWED_VALUES,
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
    return jsonify(schema), 200

def validate_request(data):
    """
    Validate incoming JSON data.
    Returns (is_valid, error_response, status_code)
    """
    if not data:
        return False, {"error": "No data provided. Please send JSON with user information."}, 400
    
    # Check for exact key match (no extra keys, no missing keys)
    received_keys = set(data.keys())
    required_keys_set = set(REQUIRED_KEYS)
    
    # Check for missing keys
    missing_keys = required_keys_set - received_keys
    if missing_keys:
        return False, {
            "error": f"Missing required keys: {sorted(missing_keys)}",
            "allowed": {"required_keys": REQUIRED_KEYS}
        }, 400
    
    # Check for extra keys
    extra_keys = received_keys - required_keys_set
    if extra_keys:
        return False, {
            "error": f"Unexpected keys found: {sorted(extra_keys)}",
            "allowed": {"required_keys": REQUIRED_KEYS}
        }, 400
    
    # Validate categorical values
    for key, allowed_list in ALLOWED_VALUES.items():
        if key in data:
            value = data[key]
            if value not in allowed_list:
                return False, {
                    "error": f"Invalid value for '{key}': '{value}'",
                    "allowed": {key: allowed_list}
                }, 400
    
    # Validate numeric fields (check they are numbers)
    numeric_fields = ["Age", "BMI", "Blood_Pressure_Systolic", "Blood_Sugar_Level", "Daily_Steps", "Exercise_Frequency"]
    for field in numeric_fields:
        if field in data:
            try:
                float(data[field])
            except (ValueError, TypeError):
                return False, {
                    "error": f"'{field}' must be a number",
                    "allowed": {"required_keys": REQUIRED_KEYS}
                }, 400
    
    return True, None, 200

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Generate diet recommendations based on user data."""
    try:
        # Check if models are loaded
        if model is None or preprocessor is None or food_df is None:
            return jsonify({
                "error": "Models not loaded. Please check server logs."
            }), 500
        
        # Get JSON data from request
        data = request.get_json()
        
        # Log request payload
        logger.info(f"Received recommendation request: {data}")
        
        # Validate request
        is_valid, error_response, status_code = validate_request(data)
        if not is_valid:
            logger.warning(f"Validation failed: {error_response}")
            return jsonify(error_response), status_code
        
        # Create DataFrame from input data
        user_df = pd.DataFrame([data])
        
        # Select only the features used in training
        try:
            user_df = user_df[features_list]
        except KeyError as e:
            logger.error(f"Invalid feature in input data: {e}")
            return jsonify({
                "error": f"Invalid feature in input data: {e}",
                "allowed": {"required_keys": REQUIRED_KEYS}
            }), 400
        
        # Preprocess the user's data
        user_processed = preprocessor.transform(user_df)
        
        # Predict the cluster
        user_cluster = model.predict(user_processed)[0]
        
        # Log predicted cluster
        logger.info(f"Predicted cluster: {user_cluster} for request payload: {data}")
        
        # Get recommendations based on cluster
        profile_name, recommendation_type, recommended_foods = get_cluster_recommendations(user_cluster)
        
        # Convert recommendations to list of dictionaries
        foods_list = recommended_foods[['Food', 'Category', 'Protein', 'Fat', 'Carbs', 'Calories']].to_dict('records')
        
        # Format numeric values properly
        for food in foods_list:
            for key in ['Protein', 'Fat', 'Carbs', 'Calories']:
                if pd.isna(food[key]):
                    food[key] = 0
                else:
                    food[key] = float(food[key])
        
        # Return JSON response
        return jsonify({
            "profile_name": profile_name,
            "recommendation_type": recommendation_type,
            "recommended_foods": foods_list
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred during recommendation: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Load models and data at startup
    if load_models_and_data():
        print("Starting Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to load models. Server not started.")

