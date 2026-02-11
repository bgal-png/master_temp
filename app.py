import streamlit as st
import pandas as pd
import os
import re

st.set_page_config(page_title="Excel Diagnostician", layout="wide")
st.title("🕵️ Column Inspector")

# --- 1. UPLOAD FILE ---
st.subheader("1. Upload your User File")
uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx'])

# --- 2. ROW SELECTOR ---
st.info("👇 Change this number until the 'Found Columns' list looks correct!")
header_row_idx = st.number_input("Header Row Number (0 = First Row)", min_value=0, max_value=10, value=0)

if uploaded_file:
    # Load the file
    try:
        df = pd.read_excel(uploaded_file, dtype=str, header=header_row_idx)
    except:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, dtype=str, sep=None, engine='python', header=header_row_idx)

    # --- MAGIC CLEANER ---
    # This removes newlines and extra spaces so we can see the "Real" names
    clean_columns = []
    for col in df.columns:
        # Replace newlines with a space, strip whitespace
        clean_col = str(col).replace('\n', ' ').strip()
        # Remove double spaces
        clean_col = re.sub(r'\s+', ' ', clean_col)
        clean_columns.append(clean_col)
    
    df.columns = clean_columns

    # --- 3. SHOW RESULTS ---
    st.divider()
    st.subheader("🔎 What the Computer Sees:")
    
    st.write(f"**Total Columns Found:** {len(clean_columns)}")
    
    # Print the list clearly
    st.code(clean_columns)
    
    st.divider()
    st.write("### 📊 First 3 Rows of Data (To verify)")
    st.dataframe(df.head(3))
