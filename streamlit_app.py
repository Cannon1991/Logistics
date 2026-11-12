import os
import re
import requests
import streamlit as st

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nigeria Postcode Hub & Geo-Shield",
    page_icon="🇳🇬",
    layout="centered",
)

# --- CONFIGURATION & SECRETS ---
# Set NIPOST_API_KEY in your environment variables or .streamlit/secrets.toml
NIPOST_API_KEY = os.getenv("NIPOST_API_KEY", "")
NIPOST_API_BASE_URL = "https://postcode.gov.ng"  # Update with exact endpoint from docs.postcode.gov.ng
WHITELISTED_IPS = {"127.0.0.1", "::1"}  # Add trusted admin or webhook IPs here


# --- 1. GEOGRAPHIC IP SCREENING (REVERSE PROXY AWARE) ---
def get_client_ip() -> str:
    """Extracts the real visitor IP from reverse proxy headers."""
    try:
        headers = st.context.headers
        # Check X-Forwarded-For first (comma-separated list; left-most is original client)
        x_forwarded_for = headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        # Fallback to X-Real-IP
        x_real_ip = headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()
    except Exception:
        pass
    return "127.0.0.1"


@st.cache_data(ttl=3600)
def resolve_ip_country(ip_address: str) -> str:
    """Resolves an IP address to its ISO 3166-1 alpha-2 country code."""
    if ip_address in WHITELISTED_IPS or ip_address.startswith(("10.", "192.168.", "172.")):
        return "NG"  # Treat local/private network traffic as allowed

    # Check if Nginx already injected the GeoIP2 country header
    try:
        nginx_country = st.context.headers.get("X-Country-Code")
        if nginx_country and len(nginx_country) == 2:
            return nginx_country.upper()
    except Exception:
        pass

    # Fallback lookup via ip-api.com (replace with local MaxMind GeoLite2 DB in high-traffic production)
    try:
        response = requests.get(f"http://ip-api.com{ip_address}?fields=status,countryCode", timeout=3)
        data = response.json()
        if data.get("status") == "success":
            return data.get("countryCode", "UNKNOWN")
    except requests.RequestException:
        pass

    return "UNKNOWN"


def enforce_nigeria_geoblock():
    """Blocks access if the request originates outside Nigeria (NG)."""
    client_ip = get_client_ip()
    country_code = resolve_ip_country(client_ip)

    if country_code != "NG":
        st.error("🚫 **403 Access Denied: Geographic Restriction Active**")
        st.write(
            "This platform is restricted to traffic originating within **Nigeria (NG)**."
        )
        st.caption(f"Detected IP: `{client_ip}` | Resolved Region: `{country_code}`")
        st.stop()

    return client_ip, country_code


# --- 2. NIGERIA POSTCODE VALIDATION & API LOOKUP ---
def validate_ndaps_format(code: str) -> bool:
    """Validates Nigeria's 11-character alphanumeric postcode format."""
    cleaned = code.strip().upper().replace("-", "").replace(" ", "")
    return bool(re.match(r"^[A-Z0-9]{11}$", cleaned))


def lookup_postcode(postcode: str) -> dict:
    """Queries the NIPOST Postcode API or returns a simulated response if no API key is set."""
    cleaned_code = postcode.strip().upper().replace("-", "").replace(" ", "")

    if NIPOST_API_KEY:
        headers = {
            "Authorization": f"Bearer {NIPOST_API_KEY}",
            "Accept": "application/json",
        }
        response = requests.get(
            f"{NIPOST_API_BASE_URL}/postcodes/{cleaned_code}",
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        return response.json()

    # Demo / Staging Mock Response when NIPOST_API_KEY is not configured
    return {
        "status": "simulated_demo",
        "postcode": cleaned_code,
        "state": "Lagos",
        "lga": "Eti-Osa",
        "district": "Victoria Island",
        "street": "Adetokunbo Ademola Street",
        "building_type": "Commercial / Mixed Use",
        "coordinates": {"latitude": 6.4311, "longitude": 3.4245},
    }


# --- 3. MAIN STREAMLIT UI ---
def main():
    # Run Geo-Block check before rendering app content
    client_ip, country_code = enforce_nigeria_geoblock()

    st.title("🇳🇬 Nigeria Digital Postcode Hub")
    st.markdown(
        "Verify **11-character NDAPS building postcodes** for logistics, fintech KYC, and emergency dispatch."
    )

    with st.sidebar:
        st.header("🛡️ Geo-Shield Status")
        st.success(f"**Access Granted ({country_code})**")
        st.caption(f"Client IP: `{client_ip}`")
        st.divider()
        st.subheader("API Mode")
        if NIPOST_API_KEY:
            st.info("Connected to Live NIPOST API")
        else:
            st.warning("Demo Mode (Set `NIPOST_API_KEY` env var for live data)")

    # Postcode Lookup Form
    with st.form("postcode_form"):
        raw_code = st.text_input(
            "Enter 11-Character Building Postcode",
            placeholder="e.g., LA101234567",
            max_chars=13,
        )
        submitted = st.form_submit_button("Verify & Resolve Address", type="primary")

    if submitted:
        if not validate_ndaps_format(raw_code):
            st.error(
                "Invalid format. Please enter a valid **11-character alphanumeric** Nigeria Postcode."
            )
        else:
            with st.spinner("Resolving building coordinates..."):
                try:
                    result = lookup_postcode(raw_code)
                    st.success(f"Verified Postcode: **{result['postcode']}**")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("State", result.get("state", "N/A"))
                        st.write(f"**LGA:** {result.get('lga', 'N/A')}")
                        st.write(f"**District:** {result.get('district', 'N/A')}")
                    with col2:
                        st.metric("Building Type", result.get("building_type", "N/A"))
                        st.write(f"**Street:** {result.get('street', 'N/A')}")
                        coords = result.get("coordinates", {})
                        st.write(
                            f"**Lat/Lon:** `{coords.get('latitude')}, {coords.get('longitude')}`"
                        )

                    if "coordinates" in result:
                        st.map(
                            [
                                {
                                    "lat": result["coordinates"]["latitude"],
                                    "lon": result["coordinates"]["longitude"],
                                }
                            ]
                        )

                except requests.HTTPError as e:
                    st.error(f"API Lookup Failed: {e}")
                except Exception as e:
                    st.error(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
