import streamlit as st
import pandas as pd
from thefuzz import fuzz
import io

# 1. Page Configuration
st.set_page_config(page_title="Excel Spellchecker", layout="wide")
st.title("Excel Spellchecker (Fixed Ignored Columns)")

# --- 2. CONFIGURATION ---
# We define the columns to ignore here. 
# The code will look for these exact names (trimmed of spaces).
DEFAULT_IGNORE = [
    "Glasses name", 
    "Meta description", 
    "XML description", 
    "Glasses model", 
    "Glasses color code"
]

# --- 3. HELPER FUNCTION ---
def load_and_clean(file_path_or_buffer):
    """
    Loads Excel and cleans headers to ensure matching works.
    Removes leading/trailing spaces from column names.
    """
    df = pd.read_excel(file_path_or_buffer, dtype=str)
    # Strip whitespace from column names to match the Ignore List
    df.columns = [str(c).strip() for c in df.columns]
    return df

# 4. Load Master File
try:
    master_df = load_and_clean("master.xlsx")
    st.success("✅ Master Database Loaded.")
except Exception as e:
    st.error(f"❌ Could not find 'master.xlsx'. Error: {e}")
    st.stop()

# 5. User Upload
st.divider()
st.subheader("1. Upload your file")
uploaded_file = st.file_uploader("Choose your Excel file", type=['xlsx'])

if uploaded_file:
    user_df = load_and_clean(uploaded_file)
    st.info(f"Uploaded file has {len(user_df)} rows.")

    # 6. Settings
    st.divider()
    st.subheader("2. Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        # Only show columns that exist in both files
        common_cols = [c for c in master_df.columns if c in user_df.columns]
        if not common_cols:
            st.error("No matching columns found!")
            st.stop()
        id_col = st.selectbox("Unique ID Column", common_cols)

    with col2:
        threshold = st.slider("Fuzzy Match Strictness", 50, 100, 85)

    # --- IGNORE LOGIC ---
    # We pre-select the DEFAULT_IGNORE columns if they exist in the user file
    valid_defaults = [c for c in DEFAULT_IGNORE if c in user_df.columns]
    
    ignore_cols = st.multiselect(
        "Columns to IGNORE (Defaulted to your list):",
        options=user_df.columns,
        default=valid_defaults
    )

    if st.button("Run Check"):
        st.write("Checking... please wait.")
        
        mistakes = []
        master_indexed = master_df.set_index(id_col)
        
        # Define exactly which columns to process
        # Logic: Column is NOT the ID AND Column is NOT in the ignore list
        cols_to_check = [c for c in user_df.columns if c != id_col and c not in ignore_cols]

        for index, user_row in user_df.iterrows():
            user_id = user_row[id_col]
            
            # 1. Check ID existence
            if user_id not in master_indexed.index:
                mistakes.append({
                    "Row": index + 2,
                    "ID": user_id,
                    "Column": "ID Check",
                    "Error": "ID Missing in Master",
                    "Your Value": user_id,
                    "Master Value": "---"
                })
                continue 

            # 2. Get Master Data
            master_row = master_indexed.loc[user_id]
            if isinstance(master_row, pd.DataFrame):
                master_row = master_row.iloc[0]

            # 3. Check specific columns
            for col in cols_to_check:
                # If master doesn't have this col, skip it
                if col not in master_df.columns:
                    continue

                val_user = str(user_row[col]).strip()
                val_master = str(master_row[col]).strip()

                # EXACT MATCH -> Pass
                if val_user == val_master:
                    continue 

                # CASE MATCH -> Error
                if val_user.lower() == val_master.lower():
                    mistakes.append({
                        "Row": index + 2,
                        "ID": user_id,
                        "Column": col,
                        "Error": "Case Mismatch",
                        "Your Value": val_user,
                        "Master Value": val_master
                    })
                    continue

                # FUZZY MATCH -> Error
                score = fuzz.ratio(val_user.lower(), val_master.lower())
                if score >= threshold:
                    mistakes.append({
                        "Row": index + 2,
                        "ID": user_id,
                        "Column": col,
                        "Error": f"Typo ({score}%)",
                        "Your Value": val_user,
                        "Master Value": val_master
                    })
                else:
                    mistakes.append({
                        "Row": index + 2,
                        "ID": user_id,
                        "Column": col,
                        "Error": "Wrong Value",
                        "Your Value": val_user,
                        "Master Value": val_master
                    })

        # --- OUTPUT ---
        if mistakes:
            st.error(f"Found {len(mistakes)} issues.")
            res = pd.DataFrame(mistakes)
            st.dataframe(res, use_container_width=True)
            
            # Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                res.to_excel(writer, index=False)
                
            st.download_button("📥 Download Report", buffer, "mistakes.xlsx")
        else:
            st.success("✅ Perfect Match!")
