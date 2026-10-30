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
from translations import SWAHILI

# Page configuration (must be the first Streamlit command)
st.set_page_config(page_title="East Africa Food Insecurity", page_icon="🌍", layout="wide")
# Language selector and translation helper
language = st.sidebar.selectbox("Language / Lugha", ["English", "Kiswahili"])


def t(text):
    """Return the Kiswahili version of a text when Kiswahili is selected."""
    return SWAHILI.get(text, text) if language == "Kiswahili" else text

def csv_bytes(table):
    """Convert a table to CSV bytes that open correctly in Excel."""
    return table.to_csv(index=False).encode("utf-8-sig")

# Visual identity: one fixed colour per country in every chart
COUNTRY_COLORS = {"Ethiopia": "#1F4E79", "Kenya": "#C0392B", "Rwanda": "#E69F00",
                  "Tanzania": "#2E8B57", "Uganda": "#7B4FA3"}
px.defaults.template = "plotly_white"
px.defaults.color_discrete_map = COUNTRY_COLORS

st.markdown("""
<style>
[data-testid="stMetric"] {
    background: #F2F5F9; border-left: 5px solid #1F4E79;
    padding: 14px 18px; border-radius: 8px;
}
[data-testid="stMetricValue"] {color: #1F4E79;}
.block-container {padding-top: 2rem;}
.hero {
    background: linear-gradient(120deg, #1F4E79 0%, #2E6EA6 100%);
    color: white; padding: 28px 32px; border-radius: 12px; margin-bottom: 1.2rem;
}
.hero h1 {color: white; margin: 0 0 6px 0; font-size: 2rem;}
.hero p {margin: 0; font-size: 1.05rem; opacity: 0.92;}
</style>
""", unsafe_allow_html=True)
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
LABELS = {key: t(value) for key, value in LABELS.items()}
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
                "Predictor": PREDICTORS,
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
st.sidebar.title(t("🌍 East Africa Food Insecurity"))
st.sidebar.image("assets/strathmore_logo_transparent.png", width=110)
st.sidebar.caption(t("Companion platform to the research project, 2000–2023"))
PAGES = ["Overview", "Country explorer", "Relationships", "Model comparison",
         "Forward-looking test", "Hypothesis tests", "Prediction simulator",
         "About and limitations"]
page = st.sidebar.radio(t("Navigate"), PAGES, format_func=t)
if page == "Overview":
        st.markdown(
        f"""<div class="hero"><h1>{t("Predicting food insecurity in East Africa")}</h1>
        <p>{t("Climate and economic indicators for Kenya, Uganda, Tanzania, Rwanda and Ethiopia, "
              "2000–2023 (120 country-year observations).")}</p></div>""",
        unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric(t("Countries"), "5")
        c2.metric(t("Observations"), len(df))
        c3.metric(t("Mean undernourishment"), f"{df[TARGET].mean():.1f}%")
        fig = px.line(df, x="Year", y=TARGET, color="Country", markers=True,
                  labels={TARGET: LABELS[TARGET], "Year": t("Year"), "Country": t("Country")})
        fig.update_layout(title=t("Prevalence of undernourishment by country"), height=450)
        st.plotly_chart(fig, width="stretch")
        change = (df[df.Year == 2023].set_index("Country")[TARGET]
              - df[df.Year == 2001].set_index("Country")[TARGET]).round(1).sort_values()
        st.subheader(t("Change in undernourishment, 2001 to 2023 (percentage points)"))
        bar = px.bar(change.reset_index(), x=TARGET, y="Country", orientation="h", color="Country",
                 labels={TARGET: t("Percentage points"), "Country": t("Country")})
        bar.update_layout(showlegend=False, height=320)
        st.plotly_chart(bar, width="stretch")
        st.info(t("Undernourishment fell strongly in Ethiopia, Rwanda and Tanzania but not in "
              "Uganda or Kenya, although income rose in all five countries."))
        st.download_button(t("Download full dataset (CSV)"), csv_bytes(df),
                       file_name="east_africa_panel_2000_2023.csv", mime="text/csv")

elif page == "Country explorer":
    st.title(t("Country explorer"))
    selected = st.multiselect(t("Countries"), COUNTRIES, default=COUNTRIES)
    variable = st.selectbox(t("Indicator"), [TARGET] + PREDICTORS, format_func=lambda c: LABELS[c])
    years = st.slider(t("Years"), 2000, 2023, (2000, 2023))
    subset = df[df.Country.isin(selected) & df.Year.between(*years)]
    fig = px.line(subset, x="Year", y=variable, color="Country", markers=True,
                  labels={variable: LABELS[variable], "Year": t("Year"), "Country": t("Country")})
    st.plotly_chart(fig, width="stretch")
    st.subheader(t("Country averages over the selected years"))
    averages = (subset.groupby("Country")[[TARGET] + PREDICTORS]
                .mean().round(2).rename(columns=LABELS))
    averages.index.name = t("Country")
    st.dataframe(averages, width="stretch")
    st.download_button(t("Download selected data (CSV)"), csv_bytes(subset),
                       file_name="selected_data.csv", mime="text/csv")
    if "Rwanda" in selected and variable == "Poverty_rate_interpolated":
        st.warning(t("Rwanda has only one real poverty observation (2023); "
                     "its series is constant by construction."))
elif page == "Relationships":
    st.title(t("Relationships between indicators"))
    columns = [TARGET] + PREDICTORS
    correlation = df[columns].corr().round(3).rename(index=LABELS, columns=LABELS)
    fig = px.imshow(correlation, text_auto=True, color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, aspect="auto")
    fig.update_layout(height=550, title=t("Pearson correlation matrix"))
    st.plotly_chart(fig, width="stretch")

    predictor = st.selectbox(t("Predictor"), PREDICTORS, format_func=lambda c: LABELS[c])
    scatter = px.scatter(df, x=predictor, y=TARGET, color="Country", hover_data=["Year"],
                         labels={predictor: LABELS[predictor], TARGET: LABELS[TARGET],
                                 "Country": t("Country"), "Year": t("Year")})
    st.plotly_chart(scatter, width="stretch")
    st.caption(t("Correlations are computed on pooled data. The negative link with temperature "
                 "mainly reflects differences between countries (Rwanda is the coolest and has the "
                 "highest undernourishment), not an effect of warming."))
elif page == "Model comparison":
    st.title(t("Model comparison (random 80/20 split)"))
    results, importance, observed_vs_predicted, _ = train_random_split_models()
    results = results.copy()
    results["Model"] = results["Model"].map(t)
    st.dataframe(results.rename(columns={"Model": t("Model"),
                                         "R² (training)": t("R² (training)")}).round(3),
                 width="stretch")
    st.download_button(t("Download results (CSV)"), csv_bytes(results.round(3)),
                       file_name="model_comparison.csv", mime="text/csv")

    model_name = st.selectbox(t("Observed against predicted"),
                              [c for c in observed_vs_predicted.columns if c != "Observed"],
                              format_func=t)
    fig = px.scatter(observed_vs_predicted, x="Observed", y=model_name,
                     labels={"Observed": t("Observed (%)"), model_name: t("Predicted (%)")})
    limits = [observed_vs_predicted["Observed"].min(), observed_vs_predicted["Observed"].max()]
    fig.add_trace(go.Scatter(x=limits, y=limits, mode="lines", name=t("Perfect prediction"),
                             line=dict(dash="dash")))
    st.plotly_chart(fig, width="stretch")

    st.subheader(t("Feature importance (tree-based models)"))
    long_form = importance.melt("Predictor", var_name="Model", value_name="Importance")
    long_form["Predictor"] = long_form["Predictor"].map(LABELS)
    long_form["Model"] = long_form["Model"].map(t)
    st.plotly_chart(px.bar(long_form, x="Importance", y="Predictor", color="Model",
                           barmode="group", orientation="h",
                           labels={"Importance": t("Importance"), "Predictor": t("Predictor"),
                                   "Model": t("Model")}), width="stretch")
    st.caption(t("Importance shows how much a variable contributes to the splits, "
                 "not the direction of its effect."))
elif page == "Forward-looking test":
    st.title(t("Robustness: train on 2000–2017, test on 2018–2023"))
    table = train_temporal_models().copy()
    table["Model"] = table["Model"].map(t)
    st.dataframe(table.rename(columns={"Model": t("Model")}).round(3), width="stretch")
    st.download_button(t("Download results (CSV)"), csv_bytes(table.round(3)),
                       file_name="forward_looking_test.csv", mime="text/csv")
    st.warning(t("Accuracy drops sharply when the models must predict later years. "
                 "The random split overstates forecasting ability: the models estimate levels "
                 "well but forecast changes weakly."))
elif page == "Hypothesis tests":
    st.title(t("Tests of the research hypotheses (5% significance level)"))
    table = run_hypothesis_tests().copy()
    for column in ["Null hypothesis", "Pooled decision", "Country-effects decision"]:
        table[column] = table[column].map(t)
    table = table.rename(columns={column: t(column) for column in table.columns})
    st.dataframe(table.round(4), width="stretch")
    st.download_button(t("Download results (CSV)"), csv_bytes(table.round(4)),
                       file_name="hypothesis_tests.csv", mime="text/csv")
    st.caption(t("Pooled model: OLS on all 120 observations. The country-effects model adds a "
                 "dummy variable for each country. P-values are probably optimistic because "
                 "errors are correlated within each of the five countries."))
elif page == "Prediction simulator":
    st.title(t("Prediction simulator"))
    st.write(t("Choose a starting point, adjust the six indicators, and see what each model "
               "estimates for the prevalence of undernourishment."))

    _, _, _, trained_models = train_random_split_models()

    options = ["Sample average"] + [f"{c} (values for 2023)" for c in COUNTRIES]

    def show_option(option):
        if option == "Sample average":
            return t(option)
        return f"{option.split(' ')[0]} ({t('values for 2023')})"

    start = st.selectbox(t("Starting point"), options, format_func=show_option)
    if start == "Sample average":
        defaults = df[PREDICTORS].mean()
        context = None
    else:
        country = start.split(" ")[0]
        row = df[(df.Country == country) & (df.Year == 2023)].iloc[0]
        defaults = row[PREDICTORS]
        context = (country, float(row[TARGET]))

    st.subheader(t("Indicators"))
    inputs = {}
    columns = st.columns(2)
    for i, variable in enumerate(PREDICTORS):
        low, high = float(df[variable].min()), float(df[variable].max())
        value = float(min(max(defaults[variable], low), high))
        with columns[i % 2]:
            inputs[variable] = st.slider(LABELS[variable], low, high, value,
                                         key=f"{variable}_{start}")

    new_case = pd.DataFrame([inputs])[PREDICTORS]
    st.subheader(t("Estimated undernourishment"))
    result_columns = st.columns(3)
    for column, (name, model) in zip(result_columns, trained_models.items()):
        column.metric(t(name), f"{float(model.predict(new_case)[0]):.1f}%")

    if context:
        st.caption(t("Observed value for {country} in 2023: {value:.1f}%.").format(
            country=context[0], value=context[1]))

    st.warning(t("Illustrative tool only. The sliders are limited to the range of the study data. "
                 "The models estimate levels reasonably well (Random Forest R² = 0.77 on a random "
                 "split) but forecast year-to-year changes weakly (R² = 0.14 on 2018-2023). "
                 "They suit screening and monitoring, not precise early warning, and they do not "
                 "show causal effects."))
elif page == "About and limitations":
    st.title(t("About and limitations"))
    st.image("assets/strathmore_logo_transparent.png", width=160)
    st.markdown(t("**Study.** Final-year research project, BSc Statistics and Data Science, "
                  "Strathmore University (Bonane Mugwarhiriza Antoine, 169463). Title: *Predicting Food "
                  "Insecurity in East Africa Using Climate and Economic Indicators (2000–2023)*."))
    st.markdown(t("**Data.** World Bank (undernourishment compiled by the FAO, GDP per capita, inflation, "
                  "poverty rate, agricultural value added) and Our World in Data (rainfall and temperature "
                  "from Copernicus ERA5)."))
    st.markdown(t("**Limitations**"))
    st.markdown("- " + t("The poverty rate was missing for 82.5% of observations and was linearly interpolated. "
                         "Rwanda has only one real value (2023)."))
    st.markdown("- " + t("Undernourishment is published with about a two-year lag, which limits the period to "
                         "2000–2023."))
    st.markdown("- " + t("Only five countries and 120 observations; p-values are probably optimistic."))
    st.markdown("- " + t("The models suit screening and monitoring, not precise early warning."))