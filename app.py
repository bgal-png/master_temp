import streamlit as st
import pandas as pd
from difflib import get_close_matches

# 1. Page Configuration
st.set_page_config(page_title="Excel Validator v2", layout="wide")
st.title("Excel Validator: Glasses Edition 👓")

# --- COLUMN MAPPING CONFIGURATION ---
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
    try:
        df = pd.read_excel("master.xlsx", dtype=str, engine='openpyxl')
        df.columns = df.columns.str.strip() # Remove invisible spaces
        
        if "Items type" in df.columns:
            df = df[df["Items type"] == "Glasses"]
            return df
        else:
            st.error("❌ Critical Error: 'Items type' column not found in Master File.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error loading master.xlsx: {e}")
        st.stop()

def clean_user_file(file):
    df = pd.read_excel(file, dtype=str, engine='openpyxl')
    df.columns = df.columns.str.strip()
    return df

# 2. LOAD MASTER
master_df = load_master()
st.success(f"✅ Master File Loaded ({len(master_df)} rows).")

# 3. UPLOAD USER FILE
st.divider()
st.subheader("1. Upload File to Validate")
uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx'])

if uploaded_file:
    user_df = clean_user_file(uploaded_file)
    st.info(f"User file loaded: {len(user_df)} rows.")

    # 4. STRUCTURE CHECK (Sanity Check)
    missing_master = []
    missing_user = []

    for master_col, user_col in COLUMN_MAPPING.items():
        if master_col not in master_df.columns:
            missing_master.append(master_col)
        if user_col not in user_df.columns:
            missing_user.append(user_col)
    
    # --- DETECTIVE MODE ---
    if missing_master:
        st.error(f"❌ CRITICAL: The Master File is missing these columns:")
        st.write(missing_master)
        
        st.divider()
        st.warning("🕵️ DETECTIVE: Let's find the correct names!")
        
        all_master_cols = list(master_df.columns)
        
        for missing in missing_master:
            # Find the closest matching name in the actual file
            matches = get_close_matches(missing, all_master_cols, n=3, cutoff=0.6)
            if matches:
                st.write(f"**For '{missing}', did you mean:**")
                for match in matches:
                    st.code(match)
            else:
                st.write(f"Could not find anything similar to '{missing}'")
        
        st.stop()
        
    if missing_user:
        st.error(f"❌ CRITICAL: Your Uploaded File is missing these columns: {missing_user}")
        st.stop()
        
    st.success("✅ Structure Validated! All required columns exist.")
    
    if st.button("Start Validation"):
        st.write("Validation logic coming next...")
