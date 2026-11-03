# East Africa Food Insecurity Platform

Interactive dashboard built from the research project
"Predicting Food Insecurity in East Africa Using Climate and Economic Indicators (2000-2023)",
Strathmore University.

**Live application:** https://east-africa-food-insecurity.streamlit.app/

## What it contains
- Country explorer, correlations and charts for 5 countries (2000-2023)
- Comparison of three models and a forward-looking test (2018-2023)
- Tests of the research hypotheses
- Prediction simulator using a final Random Forest model
- English and Kiswahili interface, CSV downloads

## Limitations
The models estimate levels reasonably well but forecast year-to-year changes weakly.
They suit screening and monitoring, not precise early warning.

## Run locally
    pip install -r requirements.txt
    streamlit run app.py

## Data
World Bank (World Development Indicators, FAO-compiled undernourishment) and
Our World in Data (rainfall and temperature from Copernicus ERA5).