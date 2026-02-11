import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Excel Validator v2", layout="wide")
st.title("Excel Validator: Glasses Edition 👓")

# --- COLUMN MAPPING CONFIGURATION ---
# Key = Master File Column Name
# Value = User File Column Name
COLUMN_MAPPING = {
    "Glasses type": "Glasses type",
    "Manufacturer": "Manufacturer",
    "Glasses size: glasses width": "Glasses size: glasses width",
    "Glasses size: temple length": "Glasses size: temple length",
    "Glasses size: lens height": "Glasses size: lens height",
    "Glasses size: lens width": "Glasses size: lens width",
    "Glasses size: bridge": "Glasses size: bridge",
    "Glasses shape": "Glasses shape",
    "Glasses other info": "Glasses other info",
    "Glasses frame type": "Glasses frame type",
    "Glasses frame color": "Frame Colour",
    "Glasses temple color": "Temple Colour",
    "Glasses main material": "Glasses main material",
    "Glasses lens Color": "Glasses lens Colour",
    "Glasses lens material": "Glasses lens material",
    "Glasses lens effect": "Glasses lens effect",
    "Sunglasses filter": "Sunglasses filter",
    "Glasses genre": "Glasses gendre",
    "Glasses usable": "Glasses usable",
    "Glasses collection": "Glasses collection",
    "UV filter": "UV filter",
    "Items type": "Items type",
    "Items packing": "Items packing",
    "Glasses contain": "Glasses contain",
    "Sport Glasses": "Sports Glasses",
    "Glasses frame color effect": "Glasses frame color effect",
    "Glasses other features": "Glasses other features",
    "SunGlasses RX lenses": "SunGlasses RX lenses",
    "Glasses clip-on lens colour": "Glasses clip-on lens colour",
    "Brand": "Brand",
    "Producing company": "Producing company",
    "Glasses for your face shape": "Glasses for your face shape",
    "Glasses lenses no-orders": "Glasses lenses no-orders"
}

# --- HELPER FUNCTIONS ---
@st.cache_data
def load_master():
    """
    Loads master.xlsx using openpyxl engine.
    Filters for 'Items type' == 'Glasses'.
    """
    try:
        # engine='openpyxl' helps with compatibility
        df = pd.read_excel("master.xlsx", dtype=str, engine='openpyxl')
        
        # Clean headers (strip hidden spaces)
        df.columns = df.columns.str.strip()
        
        # Filter for 'Glasses' only (Column V in Excel, 'Items type' here)
        if "Items type" in df.columns:
            df = df[df["Items type"] == "Glasses"]
            return df
        else:
            st.error("❌ Critical Error: 'Items type' column not found in Master File.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error loading master.xlsx: {e}")
        st.info("💡 Hint: Ensure 'master.xlsx' is a valid Excel file, not a CSV renamed to .xlsx.")
        st.stop()

def clean_user_file(file):
    """
    Loads user file and strips whitespace from headers.
    """
    df = pd.read_excel(file, dtype=str, engine='openpyxl')
    df.columns = df.columns.str.strip()
    return df

# 2. LOAD MASTER DATA
master_df = load_master()
st.success(f"✅ Master File Loaded Successfully ({len(master_df)} rows of 'Glasses').")

# 3. UPLOAD USER FILE
st.divider()
st.subheader("1. Upload File to Validate")
uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx'])

if uploaded_file:
    try:
        user_df = clean_user_file(uploaded_file)
        st.info(f"User file loaded: {len(user_df)} rows.")

        # 4. STRUCTURE CHECK (Sanity Check)
        # Check if required columns exist in both files based on the Mapping
        missing_master = []
        missing_user = []

        for master_col, user_col in COLUMN_MAPPING.items():
            if master_col not in master_df.columns:
                missing_master.append(master_col)
            if user_col not in user_df.columns:
                missing_user.append(user_col)
        
        # Stop if Master is missing columns
        if missing_master:
            st.error(f"❌ CRITICAL: The Master File is missing these columns: {missing_master}")
            st.stop()
            
        # Stop if User file is missing columns
        if missing_user:
            st.error(f"❌ CRITICAL: Your Uploaded File is missing these columns: {missing_user}")
            st.stop()
            
        st.success("✅ Structure Validated! All required columns exist in both files.")
        
        # Placeholder for validation logic
        if st.button("Start Validation"):
            st.write("Validation logic is ready to be added next...")
            
    except Exception as e:
        st.error(f"❌ Error reading uploaded file: {e}")
