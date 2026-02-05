import streamlit as st
import pandas as pd
from thefuzz import fuzz
import io

# 1. Page Configuration
st.set_page_config(page_title="Excel Spellchecker", layout="wide")
st.title("My Excel Spellchecker (Smart & Clean)")

# --- HELPER: CLEAN & UNIQUE HEADERS ---
def clean_headers(df):
    """
    Cleans headers and handles duplicates.
    If two columns are named "Price", the second becomes "Price_2".
    """
    # 1. Basic Clean
    clean_names = []
    for c in df.columns:
        s = str(c).replace("\n", " ").strip()
        s = " ".join(s.split()) # Remove double spaces
        clean_names.append(s)
    
    # 2. Enforce Uniqueness
    seen = {}
    final_names = []
    for name in clean_names:
        if name in seen:
            seen[name] += 1
            final_names.append(f"{name}_{seen[name]}")
        else:
            seen[name] = 1
            final_names.append(name)
            
    df.columns = final_names
    return df

# 2. Load Master File (Cached)
@st.cache_data
def load_master():
    df = pd.read_excel("master.xlsx", dtype=str)
    df = clean_headers(df)
    return df

try:
    master_df = load_master()
    st.success("Master Database Loaded Successfully.")
except Exception as e:
    st.error(f"Could not find 'master.xlsx'. Make sure it is in the folder! Error: {e}")
    st.stop()

# 3. User Upload Section
st.divider()
st.subheader("1. Upload your file")
uploaded_file = st.file_uploader("Choose your Excel file", type=['xlsx'])

if uploaded_file:
    # Load user data
    user_df = pd.read_excel(uploaded_file, dtype=str)
    user_df = clean_headers(user_df)
    
    st.info(f"Uploaded file has {len(user_df)} rows.")

    # 4. Settings Section
    st.divider()
    st.subheader("2. Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        # Filter strictly to shared columns to avoid crashes
        common_cols = [c for c in master_df.columns if c in user_df.columns]
        if not common_cols:
            st.error("No matching columns found between files!")
            st.stop()
            
        id_col = st.selectbox("Which column contains the Unique ID?", common_cols)

    with col2:
        threshold = st.slider("Fuzzy Match Threshold (0-100)", 50, 100, 85)

    # --- IGNORE COLUMNS SECTION ---
    # Default list
    defaults = ["Glasses name", "Meta description", "XML description", "Glasses model", "Glasses color code"]
    # Only verify against the NOW CLEANED user_df columns
    valid_defaults = [c for c in defaults if c in user_df.columns]
    
    ignore_cols = st.multiselect(
        "Select columns to IGNORE (Typing removes them from check):",
        options=user_df.columns,
        default=valid_defaults
    )

    # Button to trigger check
    if st.button("Run Spellcheck Comparison"):
        
        st.write("Checking... please wait.")

        # --- PREPARE LISTS ---
        # 1. We start with ALL user columns
        # 2. We REMOVE the ID column
        # 3. We REMOVE any column inside 'ignore_cols'
        columns_to_check = [
            c for c in user_df.columns 
            if c != id_col and c not in ignore_cols
        ]
        
        # DEBUG: Verify we aren't checking ignored stuff
        # st.write(f"Checking these {len(columns_to_check)} columns: {columns_to_check}")

        mistakes = []
        master_indexed = master_df.set_index(id_col)
        
        for index, user_row in user_df.iterrows():
            user_id = user_row[id_col]
            
            # A. ID Check
            if user_id not in master_indexed.index:
                mistakes.append({
                    "Row #": index + 2,
                    "ID": user_id,
                    "Column": "ID Check",
                    "Error Type": "ID Missing",
                    "Your Value": user_id,
                    "Master Value": "Not Found"
                })
                continue 

            # B. Get Master Data
            master_row = master_indexed.loc[user_id]
            # Handle duplicate IDs in Master
            if isinstance(master_row, pd.DataFrame):
                master_row = master_row.iloc[0]

            # C. Check Columns
            for column in columns_to_check:
                
                # Only check if Master actually has this column
                if column in master_df.columns:
                    val_user = str(user_row[column]).strip()
                    val_master = str(master_row[column]).strip()
                    
                    # Exact Match (Pass)
                    if val_user == val_master:
                        continue 

                    # Case Mismatch (Error)
                    if val_user.lower() == val_master.lower():
                        mistakes.append({
                            "Row #": index + 2,
                            "ID": user_id,
                            "Column": column,
                            "Error Type": "Case Mismatch",
                            "Your Value": val_user,
                            "Master Value": val_master
                        })
                        continue

                    # Fuzzy Match / Typo (Error)
                    score = fuzz.ratio(val_user.lower(), val_master.lower())
                    
                    if score >= threshold:
                        mistakes.append({
                            "Row #": index + 2,
                            "ID": user_id,
                            "Column": column,
                            "Error Type": f"Typo ({score}%)",
                            "Your Value": val_user,
                            "Master Value": val_master
                        })
                    else:
                        mistakes.append({
                            "Row #": index + 2,
                            "ID": user_id,
                            "Column": column,
                            "Error Type": "Wrong Value",
                            "Your Value": val_user,
                            "Master Value": val_master
                        })

        # --- OUTPUT ---
        if mistakes:
            st.error(f"Found {len(mistakes)} discrepancies.")
            results_df = pd.DataFrame(mistakes)
            
            # Sort for readability
            results_df = results_df.sort_values(by=["Error Type", "Row #"])
            
            # Show on screen
            st.dataframe(results_df, use_container_width=True)
            
            # Download
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                results_df.to_excel(writer, index=False, sheet_name='Mistakes')
                
            st.download_button(
                label="📥 Download Only Mistakes",
                data=buffer,
                file_name="spellcheck_mistakes.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.balloons()
            st.success("Perfect Match! No mistakes found in the selected columns.")
