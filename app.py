import streamlit as st
import pandas as pd

# 1. Page Setup
st.set_page_config(page_title="Excel Validator v2", layout="wide")
st.title("Excel Validator: Glasses Edition 👓")

# 2. Load and Filter Master Data
@st.cache_data
def load_filtered_master():
    # Load the file
    # dtype=str ensures we keep leading zeros (e.g., '00123')
    df = pd.read_excel("master.xlsx", dtype=str)
    
    # --- CLEAN HEADERS ---
    # Strip hidden spaces from column names (Essential!)
    df.columns = df.columns.str.strip()
    
    # --- FILTER LOGIC ---
    # target column: "Items type" (Column V)
    # target value: "Glasses"
    
    target_col = "Items type"
    
    if target_col in df.columns:
        # Filter: Keep only rows where 'Items type' == 'Glasses'
        filtered_df = df[df[target_col] == "Glasses"]
        return filtered_df
    else:
        st.error(f"❌ Critical Error: Column '{target_col}' not found in Master File.")
        st.stop()

# 3. Execution
try:
    master_df = load_filtered_master()
    
    st.success(f"✅ Master File Loaded & Filtered.")
    st.write(f"Found **{len(master_df)}** rows of 'Glasses'.")
    
    # Show preview to confirm it worked
    with st.expander("👀 Preview Filtered Master Data"):
        st.dataframe(master_df.head())

except Exception as e:
    st.error(f"Could not load file: {e}")
