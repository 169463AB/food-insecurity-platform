"""East Africa Food Insecurity Platform - companion dashboard to the research project."""
import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.base import clone
import statsmodels.formula.api as smf

# Page configuration (must be the first Streamlit command)
st.set_page_config(page_title="East Africa Food Insecurity", page_icon="🌍", layout="wide")

# Names of the variables used throughout the application
TARGET = "Undernourishment_pct_final"
PREDICTORS = ["Rainfall_mm", "Temperature_C", "GDP_per_capita_USD",
              "Inflation_pct", "Poverty_rate_interpolated", "Agri_value_added_pctGDP"]
LABELS = {
    TARGET: "Undernourishment (%)",
    "Rainfall_mm": "Rainfall (mm)",
    "Temperature_C": "Temperature (°C)",
    "GDP_per_capita_USD": "GDP per capita (US$)",
    "Inflation_pct": "Inflation (%)",
    "Poverty_rate_interpolated": "Poverty rate (%)",
    "Agri_value_added_pctGDP": "Agricultural value added (% of GDP)",
}
COUNTRIES = ["Ethiopia", "Kenya", "Rwanda", "Tanzania", "Uganda"]


@st.cache_data
def load_data():
    """Read the cleaned panel dataset once and keep it in memory."""
    return pd.read_csv("data/final_panel_dataset.csv")

def compute_metrics(observed, predicted):
    """RMSE, MAE and R-squared, the three metrics used in Chapter 4."""
    return {"RMSE": float(np.sqrt(mean_squared_error(observed, predicted))),
            "MAE": float(mean_absolute_error(observed, predicted)),
            "R²": float(r2_score(observed, predicted))}


@st.cache_resource(show_spinner="Training the three models (about a minute the first time)...")
def train_random_split_models():
    """Train the three models on 80% of the data and test them on the other 20%."""
    data = load_data()
    X, y = data[PREDICTORS], data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    tree_grid = {"max_depth": [2, 3, 4, 5, 6, 8, None], "min_samples_leaf": [1, 3, 5, 10]}
    forest_grid = {"n_estimators": [200, 500], "max_depth": [None, 5, 10],
                   "min_samples_leaf": [1, 3, 5], "max_features": ["sqrt", 1.0]}

    models = {
        "Multiple Linear Regression": LinearRegression().fit(X_train, y_train),
        "Decision Tree": GridSearchCV(
            DecisionTreeRegressor(random_state=42), tree_grid, cv=5,
            scoring="neg_root_mean_squared_error").fit(X_train, y_train).best_estimator_,
        "Random Forest": GridSearchCV(
            RandomForestRegressor(random_state=42, n_jobs=-1), forest_grid, cv=5,
            scoring="neg_root_mean_squared_error", n_jobs=-1).fit(X_train, y_train).best_estimator_,
    }

    rows, predictions = [], {}
    for name, model in models.items():
        predicted = model.predict(X_test)
        predictions[name] = predicted
        row = compute_metrics(y_test, predicted)
        row["R² (training)"] = float(r2_score(y_train, model.predict(X_train)))
        rows.append({"Model": name, **row})
    results = pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)

    importance = pd.DataFrame({
        "Predictor": [LABELS[c] for c in PREDICTORS],
        "Decision Tree": models["Decision Tree"].feature_importances_,
        "Random Forest": models["Random Forest"].feature_importances_,
    })
    observed_vs_predicted = pd.DataFrame({"Observed": y_test.values, **predictions})
    return results, importance, observed_vs_predicted, models
@st.cache_resource(show_spinner="Running the forward-looking test...")
def train_temporal_models():
    """Train on 2000-2017, test on 2018-2023, reusing the hyperparameters chosen earlier."""
    data = load_data()
    train = data[data["Year"] <= 2017]
    test = data[data["Year"] >= 2018]
    _, _, _, fitted_models = train_random_split_models()

    rows = []
    for name, model in fitted_models.items():
        refit = clone(model).fit(train[PREDICTORS], train[TARGET])  # same hyperparameters
        rows.append({"Model": name,
                     **compute_metrics(test[TARGET], refit.predict(test[PREDICTORS]))})

    # Naive benchmark: each country keeps its 2017 value for every test year
    last_value = train[train["Year"] == 2017].set_index("Country")[TARGET]
    naive = test["Country"].map(last_value)
    rows.append({"Model": "Naive benchmark (2017 value)",
                 **compute_metrics(test[TARGET], naive)})
    return pd.DataFrame(rows).sort_values("RMSE").reset_index(drop=True)
@st.cache_data
def run_hypothesis_tests():
    """F-tests of H01-H04 on the pooled model and on the model with country effects."""
    data = load_data().rename(columns={
        TARGET: "Y", "Rainfall_mm": "Rain", "Temperature_C": "Temp",
        "GDP_per_capita_USD": "GDP", "Inflation_pct": "Infl",
        "Poverty_rate_interpolated": "Poverty", "Agri_value_added_pctGDP": "Agri"})
    formula = "Y ~ Rain + Temp + GDP + Infl + Poverty + Agri"
    pooled = smf.ols(formula, data).fit()
    with_country_effects = smf.ols(formula + " + C(Country)", data).fit()

    hypotheses = {
        "H01 (climate: rainfall, temperature)": "Rain = 0, Temp = 0",
        "H02 (economic: GDP, inflation, poverty)": "GDP = 0, Infl = 0, Poverty = 0",
        "H03 (agricultural value added)": "Agri = 0",
        "H04 (all six indicators)": "Rain = 0, Temp = 0, GDP = 0, Infl = 0, Poverty = 0, Agri = 0",
    }
    rows = []
    for name, restriction in hypotheses.items():
        a = pooled.f_test(restriction)
        b = with_country_effects.f_test(restriction)
        rows.append({
            "Null hypothesis": name,
            "Pooled F": float(a.fvalue), "Pooled p": float(a.pvalue),
            "Pooled decision": "Reject" if a.pvalue < 0.05 else "Do not reject",
            "Country-effects F": float(b.fvalue), "Country-effects p": float(b.pvalue),
            "Country-effects decision": "Reject" if b.pvalue < 0.05 else "Do not reject"})
    return pd.DataFrame(rows)
df = load_data()

# Sidebar navigation
st.sidebar.title("🌍 East Africa Food Insecurity")
st.sidebar.caption("Companion platform to the research project, 2000–2023")
page = st.sidebar.radio("Navigate", ["Overview", "Country explorer", "Relationships",
                                      "Model comparison", "Forward-looking test",
                                      "Hypothesis tests", "Prediction simulator",
                                      "About and limitations"])
if page == "Overview":
    st.title("Predicting food insecurity in East Africa")
    st.write("Climate and economic indicators for Kenya, Uganda, Tanzania, Rwanda and Ethiopia, "
             "2000–2023 (120 country-year observations).")
    c1, c2, c3 = st.columns(3)
    c1.metric("Countries", "5")
    c2.metric("Observations", len(df))
    c3.metric("Mean undernourishment", f"{df[TARGET].mean():.1f}%")
    fig = px.line(df, x="Year", y=TARGET, color="Country", markers=True,
                  labels={TARGET: LABELS[TARGET]})
    fig.update_layout(title="Prevalence of undernourishment by country", height=450)
    st.plotly_chart(fig, width="stretch")
    change = (df[df.Year == 2023].set_index("Country")[TARGET]
              - df[df.Year == 2001].set_index("Country")[TARGET]).round(1).sort_values()
    st.subheader("Change in undernourishment, 2001 to 2023 (percentage points)")
    st.bar_chart(change)
    st.info("Undernourishment fell strongly in Ethiopia, Rwanda and Tanzania but not in "
            "Uganda or Kenya, although income rose in all five countries.")

elif page == "Country explorer":
    st.title("Country explorer")
    selected = st.multiselect("Countries", COUNTRIES, default=COUNTRIES)
    variable = st.selectbox("Indicator", [TARGET] + PREDICTORS, format_func=lambda c: LABELS[c])
    years = st.slider("Years", 2000, 2023, (2000, 2023))
    subset = df[df.Country.isin(selected) & df.Year.between(*years)]
    fig = px.line(subset, x="Year", y=variable, color="Country", markers=True,
                  labels={variable: LABELS[variable]})
    st.plotly_chart(fig, width="stretch")
    st.subheader("Country averages over the selected years")
    averages = (subset.groupby("Country")[[TARGET] + PREDICTORS]
                .mean().round(2).rename(columns=LABELS))
    st.dataframe(averages, width="stretch")
    if "Rwanda" in selected and variable == "Poverty_rate_interpolated":
        st.warning("Rwanda has only one real poverty observation (2023); "
                   "its series is constant by construction.")
elif page == "Relationships":
    st.title("Relationships between indicators")
    columns = [TARGET] + PREDICTORS
    correlation = df[columns].corr().round(3).rename(index=LABELS, columns=LABELS)
    fig = px.imshow(correlation, text_auto=True, color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, aspect="auto")
    fig.update_layout(height=550, title="Pearson correlation matrix")
    st.plotly_chart(fig, width="stretch")

    predictor = st.selectbox("Predictor", PREDICTORS, format_func=lambda c: LABELS[c])
    scatter = px.scatter(df, x=predictor, y=TARGET, color="Country", hover_data=["Year"],
                         labels={predictor: LABELS[predictor], TARGET: LABELS[TARGET]})
    st.plotly_chart(scatter, width="stretch")
    st.caption("Correlations are computed on pooled data. The negative link with temperature "
               "mainly reflects differences between countries (Rwanda is the coolest and has the "
               "highest undernourishment), not an effect of warming.")
elif page == "Model comparison":
    st.title("Model comparison (random 80/20 split)")
    results, importance, observed_vs_predicted, _ = train_random_split_models()
    st.dataframe(results.round(3), width="stretch")

    model_name = st.selectbox("Observed against predicted",
                              [c for c in observed_vs_predicted.columns if c != "Observed"])
    fig = px.scatter(observed_vs_predicted, x="Observed", y=model_name,
                     labels={"Observed": "Observed (%)", model_name: "Predicted (%)"})
    limits = [observed_vs_predicted["Observed"].min(), observed_vs_predicted["Observed"].max()]
    fig.add_trace(go.Scatter(x=limits, y=limits, mode="lines", name="Perfect prediction",
                             line=dict(dash="dash")))
    st.plotly_chart(fig, width="stretch")

    st.subheader("Feature importance (tree-based models)")
    long_form = importance.melt("Predictor", var_name="Model", value_name="Importance")
    st.plotly_chart(px.bar(long_form, x="Importance", y="Predictor", color="Model",
                           barmode="group", orientation="h"), width="stretch")
    st.caption("Importance shows how much a variable contributes to the splits, "
               "not the direction of its effect.")
elif page == "Forward-looking test":
    st.title("Robustness: train on 2000–2017, test on 2018–2023")
    st.dataframe(train_temporal_models().round(3), width="stretch")
    st.warning("Accuracy drops sharply when the models must predict later years. "
               "The random split overstates forecasting ability: the models estimate levels "
               "well but forecast changes weakly.")
elif page == "Hypothesis tests":
    st.title("Tests of the research hypotheses (5% significance level)")
    st.dataframe(run_hypothesis_tests().round(4), width="stretch")
    st.caption("Pooled model: OLS on all 120 observations. The country-effects model adds a "
               "dummy variable for each country. P-values are probably optimistic because "
               "errors are correlated within each of the five countries.")
elif page == "Prediction simulator":
    st.title("Prediction simulator")
    st.write("Choose a starting point, adjust the six indicators, and see what each model "
             "estimates for the prevalence of undernourishment.")

    _, _, _, trained_models = train_random_split_models()

    start = st.selectbox("Starting point",
                         ["Sample average"] + [f"{c} (values for 2023)" for c in COUNTRIES])
    if start == "Sample average":
        defaults = df[PREDICTORS].mean()
        context = None
    else:
        country = start.split(" ")[0]
        row = df[(df.Country == country) & (df.Year == 2023)].iloc[0]
        defaults = row[PREDICTORS]
        context = (country, float(row[TARGET]))

    st.subheader("Indicators")
    inputs = {}
    columns = st.columns(2)
    for i, variable in enumerate(PREDICTORS):
        low, high = float(df[variable].min()), float(df[variable].max())
        value = float(min(max(defaults[variable], low), high))
        with columns[i % 2]:
            inputs[variable] = st.slider(LABELS[variable], low, high, value,
                                         key=f"{variable}_{start}")

    new_case = pd.DataFrame([inputs])[PREDICTORS]
    st.subheader("Estimated undernourishment")
    result_columns = st.columns(3)
    for column, (name, model) in zip(result_columns, trained_models.items()):
        column.metric(name, f"{float(model.predict(new_case)[0]):.1f}%")

    if context:
        st.caption(f"Observed value for {context[0]} in 2023: {context[1]:.1f}%.")

    st.warning("Illustrative tool only. The sliders are limited to the range of the study data. "
               "The models estimate levels reasonably well (Random Forest R² = 0.77 on a random "
               "split) but forecast year-to-year changes weakly (R² = 0.14 on 2018-2023). "
               "They suit screening and monitoring, not precise early warning, and they do not "
               "show causal effects.")
elif page == "About and limitations":
    st.title("About and limitations")
    st.markdown("""
**Study.** Final-year research project, BSc Statistics and Data Science, Strathmore University
(Bonane Mugwarhiriza Antoine, 169463). Title: *Predicting Food Insecurity in East Africa Using
Climate and Economic Indicators (2000–2023)*.

**Data.** World Bank (undernourishment compiled by the FAO, GDP per capita, inflation, poverty rate,
agricultural value added) and Our World in Data (rainfall and temperature from Copernicus ERA5).

**Limitations**
- The poverty rate was missing for 82.5% of observations and was linearly interpolated.
  Rwanda has only one real value (2023).
- Undernourishment is published with about a two-year lag, which limits the period to 2000–2023.
- Only five countries and 120 observations; p-values are probably optimistic.
- The models suit screening and monitoring, not precise early warning.
""")