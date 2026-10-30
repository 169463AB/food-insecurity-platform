"""English to Kiswahili translations used by the platform."""

SWAHILI = {
    # Sidebar and menu
    "🌍 East Africa Food Insecurity": "🌍 Uhaba wa Chakula Afrika Mashariki",
    "Companion platform to the research project, 2000–2023":
        "Jukwaa shirikishi la mradi wa utafiti, 2000–2023",
    "Navigate": "Nenda kwenye",
    "Overview": "Muhtasari",
    "Country explorer": "Uchunguzi wa nchi",
    "Relationships": "Uhusiano kati ya viashiria",
    "Model comparison": "Ulinganisho wa mifano",
    "Forward-looking test": "Jaribio la kutazama mbele",
    "Hypothesis tests": "Majaribio ya dhana tete",
    "Prediction simulator": "Kikokotoo cha makadirio",
    "About and limitations": "Kuhusu na mapungufu",

    # Indicator labels
    "Undernourishment (%)": "Upungufu wa lishe (%)",
    "Rainfall (mm)": "Mvua (mm)",
    "Temperature (°C)": "Joto (°C)",
    "GDP per capita (US$)": "Pato la Taifa kwa kila mtu (US$)",
    "Inflation (%)": "Mfumuko wa bei (%)",
    "Poverty rate (%)": "Kiwango cha umaskini (%)",
    "Agricultural value added (% of GDP)": "Thamani iliyoongezwa ya kilimo (% ya Pato la Taifa)",

    # Common words
    "Year": "Mwaka",
    "Country": "Nchi",
    "Countries": "Nchi",
    "Observations": "Uchunguzi",

    # Overview page
    "Predicting food insecurity in East Africa": "Kutabiri uhaba wa chakula Afrika Mashariki",
    "Climate and economic indicators for Kenya, Uganda, Tanzania, Rwanda and Ethiopia, "
    "2000–2023 (120 country-year observations).":
        "Viashiria vya hali ya hewa na uchumi kwa Kenya, Uganda, Tanzania, Rwanda na Ethiopia, "
        "2000–2023 (uchunguzi 120 wa nchi na mwaka).",
    "Mean undernourishment": "Wastani wa upungufu wa lishe",
    "Prevalence of undernourishment by country": "Kiwango cha upungufu wa lishe kwa nchi",
    "Change in undernourishment, 2001 to 2023 (percentage points)":
        "Mabadiliko ya upungufu wa lishe, 2001 hadi 2023 (pointi za asilimia)",
    "Undernourishment fell strongly in Ethiopia, Rwanda and Tanzania but not in "
    "Uganda or Kenya, although income rose in all five countries.":
        "Upungufu wa lishe ulipungua kwa kiasi kikubwa nchini Ethiopia, Rwanda na Tanzania, "
        "lakini si nchini Uganda wala Kenya, ingawa mapato yaliongezeka katika nchi zote tano.",

    # Country explorer page
    "Indicator": "Kiashiria",
    "Years": "Miaka",
    "Country averages over the selected years": "Wastani wa nchi katika miaka iliyochaguliwa",
    "Rwanda has only one real poverty observation (2023); its series is constant by construction.":
        "Rwanda ina kipimo kimoja tu halisi cha umaskini (2023); mfululizo wake ni thabiti "
        "kutokana na jinsi ulivyokokotolewa.",

    # Relationships page
    "Relationships between indicators": "Uhusiano kati ya viashiria",
    "Pearson correlation matrix": "Matriki ya uhusiano wa Pearson",
    "Predictor": "Kiashiria cha kutabiri",
    "Correlations are computed on pooled data. The negative link with temperature "
    "mainly reflects differences between countries (Rwanda is the coolest and has the "
    "highest undernourishment), not an effect of warming.":
        "Uhusiano huu unakokotolewa kwa data zilizounganishwa. Uhusiano hasi na joto "
        "unaonyesha hasa tofauti kati ya nchi (Rwanda ina baridi zaidi na ina upungufu wa "
        "lishe mkubwa zaidi), si athari ya ongezeko la joto.",
    
    # Model names and table headers
    "Multiple Linear Regression": "Rejeshi la mstari la vigeu vingi",
    "Decision Tree": "Mti wa maamuzi",
    "Random Forest": "Msitu wa nasibu",
    "Naive benchmark (2017 value)": "Kipimo cha msingi rahisi (thamani ya 2017)",
    "Model": "Mfano",
    "R² (training)": "R² (mafunzo)",

    # Model comparison page
    "Model comparison (random 80/20 split)": "Ulinganisho wa mifano (mgawanyo wa nasibu 80/20)",
    "Observed against predicted": "Iliyoonekana dhidi ya iliyotabiriwa",
    "Observed (%)": "Iliyoonekana (%)",
    "Predicted (%)": "Iliyotabiriwa (%)",
    "Perfect prediction": "Utabiri kamili",
    "Feature importance (tree-based models)": "Umuhimu wa viashiria (mifano ya miti)",
    "Importance": "Umuhimu",
    "Importance shows how much a variable contributes to the splits, "
    "not the direction of its effect.":
        "Umuhimu unaonyesha kiasi ambacho kigeu kinachangia katika migawanyiko, "
        "si mwelekeo wa athari yake.",

    # Forward-looking test page
    "Robustness: train on 2000–2017, test on 2018–2023":
        "Uthabiti: mafunzo 2000–2017, jaribio 2018–2023",
    "Accuracy drops sharply when the models must predict later years. "
    "The random split overstates forecasting ability: the models estimate levels "
    "well but forecast changes weakly.":
        "Usahihi hushuka sana mifano inapolazimika kutabiri miaka ya baadaye. "
        "Mgawanyo wa nasibu unakadiria ujuzi wa kutabiri kupita kiasi: mifano inakadiria "
        "viwango vizuri lakini inatabiri mabadiliko kwa udhaifu.",

    # Hypothesis tests page
    "Tests of the research hypotheses (5% significance level)":
        "Majaribio ya dhana tete za utafiti (kiwango cha umuhimu 5%)",
    "Null hypothesis": "Dhana tete tupu",
    "H01 (climate: rainfall, temperature)": "H01 (hali ya hewa: mvua, joto)",
    "H02 (economic: GDP, inflation, poverty)":
        "H02 (uchumi: Pato la Taifa, mfumuko wa bei, umaskini)",
    "H03 (agricultural value added)": "H03 (thamani iliyoongezwa ya kilimo)",
    "H04 (all six indicators)": "H04 (viashiria vyote sita)",
    "Pooled F": "F (iliyounganishwa)",
    "Pooled p": "p (iliyounganishwa)",
    "Pooled decision": "Uamuzi (iliyounganishwa)",
    "Country-effects F": "F (athari za nchi)",
    "Country-effects p": "p (athari za nchi)",
    "Country-effects decision": "Uamuzi (athari za nchi)",
    "Reject": "Imekataliwa",
    "Do not reject": "Haikataliwi",
    "Pooled model: OLS on all 120 observations. The country-effects model adds a "
    "dummy variable for each country. P-values are probably optimistic because "
    "errors are correlated within each of the five countries.":
        "Mfano uliounganishwa: OLS kwa uchunguzi wote 120. Mfano wa athari za nchi "
        "unaongeza kigeu bandia kwa kila nchi. Thamani za p huenda zimekadiriwa juu "
        "kupita kiasi kwa sababu makosa yanahusiana ndani ya kila nchi kati ya nchi tano.",
    
    # Prediction simulator page
    "Choose a starting point, adjust the six indicators, and see what each model "
    "estimates for the prevalence of undernourishment.":
        "Chagua mahali pa kuanzia, rekebisha viashiria sita, kisha uone kila mfano "
        "unakadiria nini kuhusu kiwango cha upungufu wa lishe.",
    "Starting point": "Mahali pa kuanzia",
    "Sample average": "Wastani wa sampuli",
    "values for 2023": "thamani za 2023",
    "Indicators": "Viashiria",
    "Estimated undernourishment": "Upungufu wa lishe uliokadiriwa",
    "Observed value for {country} in 2023: {value:.1f}%.":
        "Thamani iliyoonekana kwa {country} mwaka 2023: {value:.1f}%.",
    "Illustrative tool only. The sliders are limited to the range of the study data. "
    "The models estimate levels reasonably well (Random Forest R² = 0.77 on a random "
    "split) but forecast year-to-year changes weakly (R² = 0.14 on 2018-2023). "
    "They suit screening and monitoring, not precise early warning, and they do not "
    "show causal effects.":
        "Zana ya mfano tu. Vitelezi vimewekewa mipaka ya data za utafiti. Mifano "
        "inakadiria viwango kwa kiasi kizuri (Msitu wa nasibu R² = 0.77 kwenye mgawanyo wa "
        "nasibu) lakini inatabiri mabadiliko ya mwaka hadi mwaka kwa udhaifu "
        "(R² = 0.14 kwa 2018-2023). Inafaa kwa uchunguzi wa awali na ufuatiliaji, si kwa "
        "tahadhari ya mapema iliyo sahihi, na haionyeshi athari za sababu-na-matokeo.",

    # About page
    "**Study.** Final-year research project, BSc Statistics and Data Science, "
    "Strathmore University (Bonane Mugwarhiriza Antoine, 169463). Title: *Predicting Food "
    "Insecurity in East Africa Using Climate and Economic Indicators (2000–2023)*.":
        "**Utafiti.** Mradi wa utafiti wa mwaka wa mwisho, Shahada ya Sayansi katika Takwimu "
        "na Sayansi ya Data, Chuo Kikuu cha Strathmore (Bonane Mugwarhiriza Antoine, 169463). "
        "Kichwa: *Kutabiri Uhaba wa Chakula Afrika Mashariki Kwa Kutumia Viashiria vya Hali ya "
        "Hewa na Uchumi (2000–2023)*.",
    "**Data.** World Bank (undernourishment compiled by the FAO, GDP per capita, inflation, "
    "poverty rate, agricultural value added) and Our World in Data (rainfall and temperature "
    "from Copernicus ERA5).":
        "**Data.** Benki ya Dunia (upungufu wa lishe uliokusanywa na FAO, Pato la Taifa kwa "
        "kila mtu, mfumuko wa bei, kiwango cha umaskini, thamani iliyoongezwa ya kilimo) na "
        "Our World in Data (mvua na joto kutoka Copernicus ERA5).",
    "**Limitations**": "**Mapungufu**",
    "The poverty rate was missing for 82.5% of observations and was linearly interpolated. "
    "Rwanda has only one real value (2023).":
        "Kiwango cha umaskini kilikosekana kwa 82.5% ya uchunguzi na kilikadiriwa kwa njia ya "
        "mstari. Rwanda ina thamani moja tu halisi (2023).",
    "Undernourishment is published with about a two-year lag, which limits the period to "
    "2000–2023.":
        "Upungufu wa lishe huchapishwa kwa kuchelewa kwa takriban miaka miwili, jambo "
        "linalopunguza kipindi hadi 2000–2023.",
    "Only five countries and 120 observations; p-values are probably optimistic.":
        "Nchi tano tu na uchunguzi 120; thamani za p huenda zimekadiriwa juu kupita kiasi.",
    "The models suit screening and monitoring, not precise early warning.":
        "Mifano inafaa kwa uchunguzi wa awali na ufuatiliaji, si kwa tahadhari ya mapema "
        "iliyo sahihi.",
        
    "Percentage points": "Pointi za asilimia",
    
    # Download buttons
    "Download selected data (CSV)": "Pakua data zilizochaguliwa (CSV)",
    "Download full dataset (CSV)": "Pakua data zote (CSV)",
    "Download results (CSV)": "Pakua matokeo (CSV)",
}