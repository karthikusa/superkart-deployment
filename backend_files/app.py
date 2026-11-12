import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask app
superkart_api = Flask("SuperKart Sales Predictor")
superkart_api.json.sort_keys = False  # keep batch predictions in row order

# Load the serialized pipeline (preprocessing + model)
model = joblib.load("superkart_model.joblib")

FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type", "Product_Id_char",
    "Store_Age_Years", "Product_Type_Category",
]


@superkart_api.get("/")
def home():
    return "Welcome to the SuperKart Sales Prediction API!"


# Online inference: one record sent as JSON
@superkart_api.post("/v1/predict")
def predict_sales():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    sample = pd.DataFrame([{f: data[f] for f in FEATURES}])
    prediction = float(model.predict(sample)[0])
    return jsonify({"Predicted Sales": round(prediction, 2)})


# Batch inference: many records sent as a CSV file
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file in the 'file' field"}), 400

    batch = pd.read_csv(request.files["file"])
    missing = [f for f in FEATURES if f not in batch.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = model.predict(batch[FEATURES])
    return jsonify({str(i): round(float(p), 2) for i, p in enumerate(predictions)})


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
