import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add this list near your other global variables
AMENITY_COLS = [
    'balcony', 'cooker', 'shared_gym', 'shared_pool', 
    'concierge', 'covered_parking', 'kitchen_appliances', 
    'maids_room', 'private_garden', 'private_gym', 
    'private_pool', 'shared_spa', 'view_of_landmark', 
    'view_of_water', 'walk_in_closet'
]

app = Flask(__name__)
CORS(app) # lets your HTML page call this API

@app.route('/')
def home():
    return "The Dubai Real Estate API is running! Send a POST request to /predict."

# Load ONCE at startup — not on every request
model = joblib.load('dubai_model.pkl')
columns = joblib.load('model_columns.pkl')

print(f"✓ {model.n_estimators} trees ready, {len(columns)} features")

# Neighbourhood → (latitude, longitude) — from your training data
NEIGHBOURHOOD_COORDS = {
    "Al Barari": (25.0943, 55.3136),
    "Business Bay": (25.1851, 55.2708),
    "Downtown Dubai": (25.1972, 55.2744),
    "Dubai Marina": (25.0772, 55.1374),
    "Palm Jumeirah": (25.1124, 55.1390),
    # ... all 54 in the downloaded app.py
}

QUALITY_MAP = {'Low': 0, 'Medium': 1, 'High': 2, 'Ultra': 3}

def build_feature_row(data: dict) -> pd.DataFrame:
    # Start: all 87 columns = 0
    row = {col: 0 for col in columns}

    # ── Numeric ─────────────────────────────
    neighborhood = data.get('neighborhood', 'Dubai Marina')
    lat, lon = NEIGHBOURHOOD_COORDS.get(neighborhood, (25.07, 55.13))
    row['latitude'] = lat
    row['longitude'] = lon
    row['size_in_sqft'] = float(data.get('size_in_sqft', 1000))
    row['no_of_bedrooms'] = int(data.get('no_of_bedrooms', 1))
    row['no_of_bathrooms'] = int(data.get('no_of_bathrooms', 1))
    row['quality_encoded'] = QUALITY_MAP.get(data.get('quality'), 1)

    # ── Amenities ────────────────────────────
    for amenity in AMENITY_COLS:
        row[amenity] = 1 if data.get(amenity, False) else 0

    # ── Neighbourhood one-hot ────────────────
    nbhd_col = f'nbhd_{neighborhood}'
    if nbhd_col in row: # Al Barari has no col (drop_first)
        row[nbhd_col] = 1

    # Return DataFrame in EXACT training column order
    return pd.DataFrame([row])[columns]

     # The @app.route decorator tells Flask:
# "when someone POSTs to /predict, run this function"
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Read the JSON the frontend sent
        data = request.get_json()

        # 2. Build the 87-column feature row
        feature_row = build_feature_row(data)

        # 3. Run the model
        prediction = model.predict(feature_row)[0]

        # 4. Round to nearest AED 1,000
        price = round(float(prediction) / 1000) * 1000

        # 5. Return result as JSON
        return jsonify({
            'predicted_price': price,
            'formatted': f"AED {price:,.0f}",
            'neighborhood': data.get('neighborhood'),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)