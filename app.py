import streamlit as st
import pandas as pd
import os
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
    "Glasses lens color": "Glasses lens Colour",
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
    "Sport glasses": "Sports Glasses",
    "Glasses frame color effect": "Glasses frame color effect",
    "Glasses other features": "Glasses other features",
    "SunGlasses RX lenses": "SunGlasses RX lenses",
    "Glasses clip-on lens color": "Glasses clip-on lens colour",
    "Brand": "Brand",
    "Producing company": "Producing company",
    "Glasses for your face shape": "Glasses for your face shape",
    "Glasses lenses no-orders": "Glasses lenses no-orders"
}

# --- HELPER FUNCTIONS ---
@st.cache_data
def load_master():
    """Robust loader for Master File."""
    file_path = "master.xlsx"
    if not os.path.exists(file_path):
        st.error("❌ 'master.xlsx' not found."); st.stop()
        
    try:
        df = pd.read_excel(file_path, dtype=str, engine='openpyxl')
    except:
        try:
            df = pd.read_csv(file_path, dtype=str, sep=None, engine='python')
        except Exception as e:
            st.error(f"❌ Could not load Master file. Error: {e}"); st.stop()
            
    df.columns = df.columns.str.strip()
    if "Items type" in df.columns:
        return df[df["Items type"] == "Glasses"]
    else:
        st.error("❌ 'Items type' column missing in Master."); st.stop()

def clean_user_file(file, header_row=0):
    """Loads user file with specific header row."""
    try:
        df = pd.read_excel(file, dtype=str, header=header_row)
    except:
        file.seek(0)
        df = pd.read_csv(file, dtype=str, sep=None, engine='python', header=header_row)
    
    # Clean headers: Convert to string and strip whitespace
    df.columns = df.columns.astype(str).str.strip()
    return df

# 2. LOAD MASTER
master_df = load_master()
st.success(f"✅ Master File Loaded ({len(master_df)} rows).")

# 3. UPLOAD SECTION
st.divider()
st.subheader("1. Upload File")

col_upload, col_settings = st.columns([2, 1])

with col_settings:
    st.info("👇 If columns aren't found, try changing this!")
    header_row_idx = st.number_input("Header Row Number (0 = First Row)", min_value=0, max_value=10, value=0)

with col_upload:
    uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx'])

if uploaded_file:
    user_df = clean_user_file(uploaded_file, header_row=header_row_idx)
    st.info(f"User file loaded: {len(user_df)} rows.")

    # --- DEBUG VIEW: SHOW WHAT WE FOUND ---
    with st.expander("🕵️ Debug: Check your Columns", expanded=False):
        st.write("The code sees these columns in your file:")
        st.code(list(user_df.columns))
        st.write("First 3 rows of data:")
        st.dataframe(user_df.head(3))

    # 4. STRUCTURE CHECK
    missing_master = [col for col in COLUMN_MAPPING.keys() if col not in master_df.columns]
    missing_user = [col for col in COLUMN_MAPPING.values() if col not in user_df.columns]

    if missing_master:
        st.error(f"❌ CRITICAL: Master File is missing: {missing_master}")
        st.stop()
        
    if missing_user:
        st.error(f"❌ CRITICAL: Your Uploaded File is missing columns!")
        st.write("We are looking for these exact names:", missing_user)
        
        # Detective Work
        st.warning("🕵️ Let's see what we found instead...")
        all_user_cols = list(user_df.columns)
        for missing in missing_user:
            matches = get_close_matches(missing, all_user_cols, n=1, cutoff=0.6)
            if matches:
                st.write(f"For '{missing}', did you have '{matches[0]}'?")
        st.stop()
        
    st.success("✅ Structure Validated! All columns match.")
    
    if st.button("Start Validation"):
        st.write("Ready for validation logic...")
