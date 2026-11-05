import streamlit as st
import re

# Set page configuration
st.set_page_config(
    page_title="Nigeria Digital Postcode Validator",
    page_icon="🇳🇬",
    layout="wide"
)

# App Title & Header
st.title("🇳🇬 Nigeria National Digital Postcode Explorer")
st.caption("Prototype tool aligned with the 11-character Alphanumeric Geospatial Postcode System (Launched October 2026)")

# Sidebar Documentation
st.sidebar.header("About the New System")
st.sidebar.markdown('''
The **11-character National Digital Alphanumeric Postcode System** replaces legacy 6-digit numeric codes with high-precision geospatial parsing:

1. **State:** Characters 1-2 (e.g., `LA` = Lagos)
2. **LGA:** Characters 3-4 (e.g., `IK` = Ikeja)
3. **District:** Characters 5-6
4. **Area:** Characters 7-8
5. **Building:** Characters 9-11 (Exact structure point)
''')

st.sidebar.info("💡 Integrate this validation into your checkout pages, KYC forms, and logistics dispatch engines via NIPOST API portals.")

# Main Interface Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Code Validator & Parser", "🛠️ Mock API Generator", "🚀 Business Use Cases"])

with tab1:
    st.subheader("Validate and Decode an 11-Digit Postcode")
    st.write("Enter an alphanumeric postcode to simulate structural lookup parsing.")
    
    # Sample Input
    sample_code = "LAIK05AR012"
    user_input = st.text_input("Enter 11-character Postcode:", value=sample_code, max_chars=11).upper().strip()
    
    if st.button("Decode & Verify Address"):
        # Basic validation rule: 11 characters, alphanumeric
        if len(user_input) != 11:
            st.error(f"❌ Invalid Length: The postcode must be exactly 11 characters. Current length: {len(user_input)}")
        elif not re.match(r"^[A-Z0-9]+$", user_input):
            st.error("❌ Invalid Characters: The postcode must contain only alphanumeric characters (A-Z, 0-9).")
        else:
            st.success("✅ Format Validated successfully!")
            
            # Deconstruct the component layers
            state_part = user_input[0:2]
            lga_part = user_input[2:4]
            district_part = user_input[4:6]
            area_part = user_input[6:8]
            building_part = user_input[8:11]
            
            st.markdown("### 🗺️ Geospatial Breakdown")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(label="State Code", value=state_part)
            with col2:
                st.metric(label="LGA Zone", value=lga_part)
            with col3:
                st.metric(label="District", value=district_part)
            with col4:
                st.metric(label="Area Block", value=area_part)
            with col5:
                st.metric(label="Building Point", value=building_part)
                
            st.info(f"📍 **Mock Resolution:** This code resolves to Building Node **#{building_part}** inside Area **{area_part}**, District **{district_part}** within Local Government Area **{lga_part}**, **{state_part} State**.")

with tab2:
    st.subheader("NIPOST Mock API Response Sandbox")
    st.write("Developers can preview the structural payload returned by `docs.postcode.gov.ng` endpoints.")
    
    mock_json = f'''{{
  "status": "success",
  "data": {{
    "postcode": "{user_input if len(user_input)==11 else 'LAIK05AR012'}",
    "geospatial": {{
      "latitude": 6.6018,
      "longitude": 3.3515,
      "accuracy_meters": 1.2
    }},
    "hierarchy": {{
      "state": "Lagos",
      "lga": "Ikeja",
      "district": "Allen Avenue Axis",
      "area": "Aromire Residential",
      "building_id": "Unit-012"
    }},
    "formatted_address": "Building 012, Aromire Residential, Allen District, Ikeja LGA, Lagos State, Nigeria."
  }}
}}'''
    st.code(mock_json, language="json")
    st.caption("⚡ Pro-tip: Pass this JSON into your internal inventory tracking or route-optimization models.")

with tab3:
    st.subheader("💡 Build-on-Postcode Solution Blueprint")
    
    use_case = st.selectbox(
        "Select your Industry Sector:",
        ["Logistics & Last-Mile Delivery", "Fintech Address Verification (KYC)", "Emergency Services Dispatch"]
    )
    
    if use_case == "Logistics & Last-Mile Delivery":
        st.markdown('''
        * **Problem:** Driver call-backs, lost hours looking for landmarks, failed second-attempts.
        * **Solution:** Replace free-text address inputs with an **11-character verified text-field**. Plot the exact target latitude/longitude directly on delivery route-maps.
        ''')
    elif use_case == "Fintech Address Verification (KYC)":
        st.markdown('''
        * **Problem:** Expensive physical tier-3 address validation, unverified agent banking operations.
        * **Solution:** Instantly match user-asserted identity records against NIPOST geospatial building databases to approve credit limits on the spot.
        ''')
    elif use_case == "Emergency Services Dispatch":
        st.markdown('''
        * **Problem:** Ambiguous location descriptions during critical fire, health, or security emergencies.
        * **Solution:** Dispatch teams directly to building nodes pinpointed by specific digital postcodes, reducing emergency response windows drastically.
        ''')
