import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# PAGE CONFIGURATION
# ----------------------------
st.set_page_config(
    page_title="Global EcoFootprint",
    page_icon="🌍",
    layout="centered"
)

# ----------------------------
# HEADER & INTRODUCTION
# ----------------------------
st.title("🌍 EcoFootprint: Global Carbon Calculator")
st.markdown("""
Understanding your personal impact is the first step towards meaningful climate action.
This calculator estimates your annual carbon footprint based on your lifestyle choices.

*Powered by regional data and aligned with UN SDG 13: Climate Action.*
""")

# Create two columns for media
col1, col2 = st.columns(2)

# Add video to first column
with col1:
    if os.path.exists("video.mp4"):
        st.video("video.mp4")
    else:
        st.warning("Video file not found")

# Add image to second column
with col2:
    if os.path.exists("image.jpg"):
        st.image("image.jpg", caption="Carbon Footprint Pledge", use_container_width=True)
    else:
        st.warning("Image file not found")

# ----------------------------
# EMISSION FACTORS
# ----------------------------
# African grid emission factors
COUNTRY_GRID_MIX = {
    "Select Country": 0.0,
    "Nigeria (Gas-dominated)": 0.55,
    "South Africa (Coal-dominated)": 0.9,
    "Kenya (Geothermal/Hydro)": 0.3,
    "Ghana (Hydro/Gas)": 0.45,
    "Egypt (Gas-dominated)": 0.6,
    "Ethiopia (Hydro-dominated)": 0.05,
    "General Sub-Saharan Africa Avg": 0.48
}

# Global emission factors
GLOBAL_EMISSION_FACTORS = {
    # Housing (kg CO2e per unit per month)
    "electricity": 0.5,    
    "natural_gas": 2.0,     
    "heating_oil": 2.68,    
    "propane": 1.5,         
    # Transport (kg CO2e per mile/km)
    "car_gasoline": 0.31,
    "car_diesel": 0.27,
    "motorcycle": 0.11,
    "bus": 0.11,
    "train": 0.06,
    "plane_short": 0.24,
    # Diet (kg CO2e per day)
    "diet_meat_heavy": 3.3,
    "diet_typical": 1.8,
    "diet_meat_regular": 2.7,
    "diet_average": 2.5,
    "diet_vegetarian": 1.5,
    "diet_vegan": 1.2,
    # LPG
    "lpg_per_kg": 3.0
}

# ----------------------------
# CALCULATION ENGINE
# ----------------------------
def calculate_carbon_footprint(data, region="global"):
    """
    Calculates the annual carbon footprint (kg CO2e) based on user input.
    Handles both global and African regional calculations.
    """
    total_kg_co2 = 0
    breakdown = {}

    # Housing Calculations
    if region == "africa":
        grid_factor = COUNTRY_GRID_MIX[data["country"]]
        breakdown["Housing: Electricity"] = data["electricity_kwh"] * grid_factor * 12
        if "lpg_kg_per_month" in data:
            breakdown["Housing: Cooking (LPG)"] = data["lpg_kg_per_month"] * GLOBAL_EMISSION_FACTORS["lpg_per_kg"] * 12
    else:
        breakdown["Housing: Electricity"] = data["electricity_kwh"] * GLOBAL_EMISSION_FACTORS["electricity"] * 12
        breakdown["Housing: Natural Gas"] = data.get("natural_gas_therms", 0) * GLOBAL_EMISSION_FACTORS["natural_gas"] * 12
        breakdown["Housing: Heating Oil"] = data.get("heating_oil_liters", 0) * GLOBAL_EMISSION_FACTORS["heating_oil"] * 12
        breakdown["Housing: Propane"] = data.get("propane_liters", 0) * GLOBAL_EMISSION_FACTORS["propane"] * 12

    # Transport Calculations
    if region == "africa":
        breakdown["Transport: Car"] = (data.get("car_km_week", 0) * 52) * GLOBAL_EMISSION_FACTORS["car_gasoline"]
        breakdown["Transport: Motorcycle"] = (data.get("moto_km_week", 0) * 52) * GLOBAL_EMISSION_FACTORS["motorcycle"]
        breakdown["Transport: Bus/Minibus"] = (data.get("bus_km_week", 0) * 52) * GLOBAL_EMISSION_FACTORS["bus"]
    else:
        breakdown["Transport: Car"] = data.get("car_miles_week", 0) * GLOBAL_EMISSION_FACTORS["car_gasoline"] * 52
        breakdown["Transport: Bus"] = data.get("bus_miles_week", 0) * GLOBAL_EMISSION_FACTORS["bus"] * 52
        breakdown["Transport: Train"] = data.get("train_miles_week", 0) * GLOBAL_EMISSION_FACTORS["train"] * 52
    
    breakdown["Transport: Flights"] = data["flight_hours"] * 500 * GLOBAL_EMISSION_FACTORS["plane_short"]

    # Diet Calculation
    diet_map = {
        "Typical (Staples + some meat)": "diet_typical",
        "Meat regularly": "diet_meat_regular",
        "Meat-Heavy": "diet_meat_heavy",
        "Average": "diet_average",
        "Vegetarian": "diet_vegetarian",
        "Vegan": "diet_vegan"
    }
    
    diet_key = diet_map[data["diet"]]
    breakdown["Diet"] = GLOBAL_EMISSION_FACTORS[diet_key] * 365

    total_kg_co2 = sum(breakdown.values())
    return total_kg_co2, breakdown

# ----------------------------
# USER INPUT SECTION
# ----------------------------
st.header("📊 Your Lifestyle")

# Region Selection
region = st.radio("Select your region:", ["Global", "Africa"], horizontal=True)

input_data = {}

if region.lower() == "africa":
    col1, col2 = st.columns(2)
    with col1:
        input_data["country"] = st.selectbox(
            "Select your country", 
            options=list(COUNTRY_GRID_MIX.keys()), 
            help="This sets the carbon intensity of your electricity grid."
        )
    with col2:
        if input_data["country"] != "Select Country":
            factor = COUNTRY_GRID_MIX[input_data["country"]]
            st.metric(label="Your Grid's Carbon Intensity", value=f"{factor} kg CO₂/kWh")

    with st.expander("🏠 Housing & Cooking"):
        input_data["electricity_kwh"] = st.slider("Monthly electricity usage (kWh)", 0, 600, 100, 
            help="Many households use less than 100 kWh. Think lights, fan, TV, fridge.")
        
        st.markdown("**Cooking Gas (LPG)**")
        cylinder_size = st.selectbox(
            "What size is your primary gas cylinder?",
            options=[3, 6, 12, 15, 45],
            format_func=lambda x: f"{x} kg",
            help="The size is usually written on the cylinder."
        )
        cylinder_quantity = st.slider(
            f"How many {cylinder_size} kg cylinders do you use per month?",
            min_value=0.0, max_value=10.0, value=0.5, step=0.5,
            help="E.g., 0.5 means one cylinder lasts you two months."
        )
        input_data["lpg_kg_per_month"] = cylinder_size * cylinder_quantity
        st.caption(f"➡️ You use **{input_data['lpg_kg_per_month']} kg** of LPG per month.")

    with st.expander("🚗 Transport"):
        input_data["car_km_week"] = st.slider("Kilometers driven per week (personal car)", 0, 400, 0)
        input_data["moto_km_week"] = st.slider("Kilometers per week (motorcycle taxi or own)", 0, 200, 0)
        input_data["bus_km_week"] = st.slider("Kilometers per week (Bus, Matatu, Troski)", 0, 300, 50)
        input_data["flight_hours"] = st.slider("Hours flown per year", 0, 50, 0)

    with st.expander("🍽️ Diet"):
        input_data["diet"] = st.selectbox(
            "Which diet best describes you?",
            ("Typical (Staples + some meat)", "Meat regularly", "Vegetarian", "Vegan"),
            help="'Typical' reflects a diet based on cassava, yam, rice, beans, with fish or meat a few times a week."
        )

else:  # Global calculator
    with st.expander("🏠 Housing", expanded=True):
        input_data["electricity_kwh"] = st.slider("Monthly electricity usage (kWh)", 0, 2000, 300, help="Check your utility bill.")
        input_data["natural_gas_therms"] = st.slider("Monthly natural gas usage (therms)", 0, 200, 40, help="1 therm ≈ 100 cubic feet.")
        input_data["heating_oil_liters"] = st.slider("Monthly heating oil usage (liters)", 0, 500, 0)
        input_data["propane_liters"] = st.slider("Monthly propane usage (liters)", 0, 500, 0)

    with st.expander("🚗 Transport"):
        input_data["car_miles_week"] = st.slider("Miles driven per week (car)", 0, 500, 100)
        input_data["flight_hours"] = st.slider("Hours flown per year", 0, 100, 5, help="Round-trip NY to LA is ~10 hours.")
        input_data["bus_miles_week"] = st.slider("Miles traveled per week (bus)", 0, 500, 20)
        input_data["train_miles_week"] = st.slider("Miles traveled per week (train)", 0, 500, 10)

    with st.expander("🍽️ Diet"):
        input_data["diet"] = st.selectbox(
            "Which diet best describes you?",
            ("Meat-Heavy", "Average", "Vegetarian", "Vegan"),
            help="Diet has a significant impact on your carbon footprint."
        )

# ----------------------------
# CALCULATE BUTTON
# ----------------------------
calculate_button = st.button("🔄 Calculate My Footprint", type="primary")
valid_input = True if region != "Africa" or (region == "Africa" and input_data.get("country") != "Select Country") else False

if calculate_button and valid_input:
    total_emissions, breakdown_dict = calculate_carbon_footprint(input_data, region.lower())
    total_tons = total_emissions / 1000

    # ----------------------------
    # DISPLAY RESULTS
    # ----------------------------
    st.header("📈 Your Results")

    col1, col2, col3 = st.columns(3)
    col1.metric("Annual Carbon Footprint", f"{total_emissions:,.0f} kg CO₂")
    col2.metric("In Tons", f"{total_tons:,.1f} tons CO₂")
    
    if region.lower() == "africa":
        global_avg_kg = 4800  # Global average
        african_avg_kg = 1000  # African average
        comparison_to_global = (global_avg_kg - total_emissions) / 1000
        comparison_to_africa = (african_avg_kg - total_emissions) / 1000
        
        delta_text = "Global Avg"
        delta_val = comparison_to_global
        if total_emissions < 3000:
            delta_text = "African Avg"
            delta_val = comparison_to_africa
            
        col3.metric(f"Vs. {delta_text}", f"{delta_val:+.1f} tons", 
                   help=f"Global average is ~4.8 tons. African average is ~1.0 ton.")
    else:
        us_avg_kg = 16000
        comparison = (us_avg_kg - total_emissions) / 1000
        col3.metric("Vs. US Average", f"{comparison:+.1f} tons", 
                   help="US average is ~16 tons per person per year.")

    # Create visualization
    breakdown_df = pd.DataFrame(list(breakdown_dict.items()), columns=['Category', 'Emissions (kg)'])
    fig = px.pie(breakdown_df, values='Emissions (kg)', names='Category', 
                 title='Breakdown of Your Carbon Footprint',
                 color_discrete_sequence=px.colors.sequential.Emrld)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

    st.bar_chart(breakdown_df.set_index('Category'))

    # ----------------------------
    # RECOMMENDATIONS
    # ----------------------------
    st.header("💡 Your Personalized Reduction Plan")
    st.info("Based on your largest sources of emissions, here's how you can make the biggest impact:")

    recommendations = []

    # Transport recommendations
    if breakdown_dict.get("Transport: Car", 0) > 2000:
        recommendations.append(("**🚗 Reduce car travel by 20%.** Use public transport, bike, or carpool just one day a week.", 400))

    # Housing recommendations
    if breakdown_dict.get("Housing: Electricity", 0) > 1500:
        recommendations.append(("**💡 Switch to energy-efficient appliances** and LED bulbs. Consider solar if available.", 500))

    # Cooking recommendations (Africa-specific)
    if region.lower() == "africa" and breakdown_dict.get("Housing: Cooking (LPG)", 0) > 500:
        recommendations.append(("**🔥 Improve cooking efficiency.** Use a pressure cooker or hotbox to reduce LPG consumption.", 100))

    # Diet recommendations
    if breakdown_dict.get("Diet", 0) > 2000 and "Meat" in input_data["diet"]:
        recommendations.append(("**🍽️ Reduce meat consumption.** Try having one meat-free day per week.", 200))

    # Sort and display recommendations
    recommendations.sort(key=lambda x: x[1], reverse=True)
    for rec, saving in recommendations:
        st.success(f"{rec} _(Estimated savings: ~{saving:,.0f} kg CO₂/year)_")

    if not recommendations:
        st.success("🌟 Your footprint is already relatively low! Keep up the good habits and consider advocating for climate policy.")

# ----------------------------
# EDUCATIONAL FOOTER
# ----------------------------
st.markdown("---")
st.markdown("""
### ℹ️ About This Calculator
*   **Methodology:** Calculations are based on emission factors from EPA (USA), DEFRA (UK), and regional African data.
*   **Limitations:** This is an estimate. Your actual footprint may vary based on specific local factors.
*   **Purpose:** This tool is designed for educational purposes and to inspire positive climate action.
""")