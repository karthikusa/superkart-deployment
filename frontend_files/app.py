import os
import requests
import pandas as pd
import streamlit as st

# The backend is reached over the Docker network by its container name
BACKEND_URL = os.getenv("BACKEND_URL", "http://superkart-backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", page_icon="🛒")
st.title("SuperKart Sales Prediction")
st.write("Predict the total sales of a product in a store, for one product or a whole CSV file.")

online_tab, batch_tab = st.tabs(["Single prediction", "Batch prediction"])

with online_tab:
    st.subheader("Product details")
    product_weight = st.number_input("Product Weight", min_value=0.0, value=12.66)
    sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    allocated_area = st.number_input("Product Allocated Area", min_value=0.0, max_value=1.0,
                                     value=0.027, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08)
    product_id_char = st.selectbox("Product Id prefix", ["FD", "NC", "DR"])
    product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])

    st.subheader("Store details")
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
    city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
    store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2",
                                             "Departmental Store", "Food Mart"])
    store_age = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16)

    if st.button("Predict sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": sugar_content,
            "Product_Allocated_Area": allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
            if response.status_code == 200:
                st.success(f"Predicted sales: {response.json()['Predicted Sales']:,.2f}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend: {e}")

with batch_tab:
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None and st.button("Predict batch"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")},
                timeout=60,
            )
            if response.status_code == 200:
                uploaded_file.seek(0)
                results = pd.read_csv(uploaded_file)
                results["Predicted_Sales"] = list(response.json().values())
                st.success("Predictions complete")
                st.dataframe(results)
                st.download_button("Download results", results.to_csv(index=False),
                                   file_name="superkart_predictions.csv", mime="text/csv")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the backend: {e}")
