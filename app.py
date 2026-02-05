import streamlit as st
import pandas as pd
import os

st.title("🛠️ Debug Mode")

# 1. SHOW ME THE FILES
st.subheader("1. File System Check")
current_dir = os.getcwd()
st.write(f"**Current Folder:** `{current_dir}`")

files_in_folder = os.listdir(current_dir)
st.write("**Files found in this folder:**")
st.code(files_in_folder)

# 2. CHECK FOR MASTER FILE
target_file = "master.xlsx"

if target_file in files_in_folder:
    st.success(f"✅ Found '{target_file}'!")
else:
    st.error(f"❌ Cannot find '{target_file}'. Please check the exact spelling.")
    # check for case sensitivity
    for f in files_in_folder:
        if f.lower() == target_file.lower() and f != target_file:
            st.warning(f"⚠️ Found '{f}' but expected '{target_file}'. Rename your file or update the code!")

# 3. ATTEMPT LOAD
st.subheader("2. Loading Test")
if st.button("Try Loading Master File"):
    try:
        df = pd.read_excel(target_file)
        st.success("✅ File loaded successfully!")
        st.write("First 5 rows:")
        st.dataframe(df.head())
        st.write("Column Names found:")
        st.write(list(df.columns))
    except Exception as e:
        st.error(f"💥 Crashing during load: {e}")
