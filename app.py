import streamlit as st
import pandas as pd
import os
import io

# 1. Page Configuration
st.set_page_config(page_title="Excel Validator v2", layout="wide")
st.title("Excel Validator: Glasses Edition 👓")

# ==========================================
# 🔒 LOCKED SECTION: MASTER LOADER
# ==========================================
@st.cache_data
def load_master():
    """
    TRULY INDESTRUCTIBLE LOADER
    1. Tries Excel (.xlsx)
    2. If that fails (Zip Error), tries CSV with Auto-Separator.
    3. If that fails, tries CSV with comma/semicolon explicitly.
    """
    current_dir = os.getcwd()
    candidates = [f for f in os.listdir(current_dir) if (f.endswith('.xlsx') or f.endswith('.csv')) and "mistakes" not in f and not f.startswith('~$')]
    
    if not candidates:
        st.error("❌ No Master File found!"); st.stop()
    
    file_path = candidates[0]
    df = None
    
    # ATTEMPT 1: EXCEL (Standard)
    try:
        df = pd.read_excel(file_path, dtype=str, engine='openpyxl')
    except Exception:
        # ATTEMPT 2: CSV (Fallback loop)
        strategies = [
            {'sep': None, 'engine': 'python'}, # Auto-detect
            {'sep': ',', 'engine': 'c'},       # Standard Comma
            {'sep': ';', 'engine': 'c'},       # Semicolon
            {'sep': '\t', 'engine': 'c'}       # Tab
        ]
        
        for enc in ['utf-8', 'cp1252', 'latin1']:
            for strat in strategies:
                try:
                    df = pd.read_csv(
                        file_path, 
                        dtype=str, 
                        encoding=enc, 
                        on_bad_lines='skip', 
                        **strat
                    )
                    st.toast(f"ℹ️ Loaded '{file_path}' as CSV (Encoding: {enc})", icon="⚠️")
                    break
                except:
                    continue
            if df is not None:
                break
    
    if df is None:
        st.error(f"❌ Could not read '{file_path}'. Tried Excel and all CSV formats.")
        st.stop()

    df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    target_col = next((c for c in df.columns if "Items type" in c), None)
    if target_col:
        return df[df[target_col] == "Glasses"]
    else:
        st.error("❌ 'Items type' column missing in Master File."); st.stop()
# ==========================================
# 🔒 END LOCKED SECTION
# ==========================================

def clean_user_file(file):
    try:
        df = pd.read_excel(file, dtype=str, header=0)
    except:
        file.seek(0)
        df = pd.read_csv(file, dtype=str, sep=None, engine='python', header=0)
    
    df.columns = df.columns.astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    return df

# 2. LOAD MASTER
master_df = load_master()
st.success(f"✅ Master File Loaded ({len(master_df)} rows).")

# 3. UPLOAD SECTION
st.divider()
st.subheader("1. Upload User File")
uploaded_file = st.file_uploader("Choose Excel File", type=['xlsx'])

if uploaded_file:
    user_df = clean_user_file(uploaded_file)
    st.info(f"User file loaded: {len(user_df)} rows.")

    # ==========================================
    # 📑 TABS: SEPARATE THE TWO TOOLS
    # ==========================================
    tab1, tab2 = st.tabs(["📊 Data Validation", "🖼️ Image Name Checker"])

    # ------------------------------------------
    # TAB 1: EXISTING VALIDATION LOGIC
    # ------------------------------------------
    with tab1:
        # AUTO-MAPPING
        IDEAL_PAIRS = {
            "Glasses type": "Glasses type ID",
            "Manufacturer": "Manufacturer ID",
            "Glasses size: glasses width": "width ID",
            "Glasses size: temple length": "temple length ID",
            "Glasses size: lens height": "lens height ID",
            "Glasses size: lens width": "lens width ID",
            "Glasses size: bridge": "bridge ID",
            "Glasses shape": "Glasses shape ID",
            "Glasses other info": "other info ID",
            "Glasses frame type": "frame type ID",
            "Glasses frame color": "Frame Colour ID",
            "Glasses temple color": "Temple Colour ID",
            "Glasses main material": "main material ID",
            "Glasses lens color": "lens Colour ID",
            "Glasses lens material": "lens material ID",
            "Glasses lens effect": "lens effect ID",
            "Sunglasses filter": "Sunglasses filter ID",
            "Glasses genre": "Glasses gendre ID",
            "Glasses usable": "Glasses usable ID",
            "Glasses collection": "Glasses collection ID",
            "UV filter": "UV filter ID",
            "Items type": "Items type ID",
            "Items packing": "Items packing ID",
            "Glasses contain": "Glasses contain ID",
            "Sport glasses": "Sports Glasses ID",
            "Glasses frame color effect": "frame color effect ID",
            "Glasses other features": "other features ID",
            "SunGlasses RX lenses": "RX lenses ID",
            "Glasses clip-on lens color": "clip-on lens colour ID",
            "Brand": "Brand ID",
            "Producing company": "Producing company ID",
            "Glasses for your face shape": "face shape ID",
            "Glasses lenses no-orders": "no-orders ID"
        }
        
        active_map = {}
        user_cols = list(user_df.columns)
        master_cols = list(master_df.columns)
        
        for master_key, partial_user_key in IDEAL_PAIRS.items():
            real_master_col = next((c for c in master_cols if master_key in c), None)
            real_user_col = next((c for c in user_cols if partial_user_key in c), None)
            
            if real_master_col and real_user_col:
                active_map[real_master_col] = real_user_col
                
        st.write(f"🔗 Mapped **{len(active_map)}** columns automatically.")

        if st.button("🚀 Run Validation", type="primary"):
            mistakes = []
            st.write("Checking data... please wait.")
            
            # --- A. PREPARE MASTER DATA ---
            valid_values = {}
            for m_col in active_map.keys():
                raw_series = master_df[m_col].dropna().astype(str)
                exploded = raw_series.str.split(r',+').explode()
                clean_set = set(exploded.str.strip().str.lower())
                if "" in clean_set: clean_set.remove("")
                valid_values[m_col] = clean_set

            # --- B. CHECK USER DATA ---
            progress_bar = st.progress(0)
            total_rows = len(user_df)
            
            for index, row in user_df.iterrows():
                if index % 10 == 0: progress_bar.progress(min(index / total_rows, 1.0))
                
                for m_col, u_col in active_map.items():
                    raw_cell_value = str(row[u_col])
                    if raw_cell_value.lower() in ['nan', '', 'none']: continue

                    # 1. Whitespace
                    whitespace_issues = []
                    if raw_cell_value.startswith(" "): whitespace_issues.append("Leading Space")
                    if raw_cell_value.endswith(" "): whitespace_issues.append("Trailing Space")
                    if "  " in raw_cell_value: whitespace_issues.append("Double Spaces")
                    if "| " in raw_cell_value or " |" in raw_cell_value: whitespace_issues.append("Space around Separator")
                    
                    for issue in whitespace_issues:
                         mistakes.append({
                            "Row": index + 2,
                            "Column": u_col,
                            "Error Type": "Whitespace Error",
                            "Invalid Value": issue,
                            "Full Cell Content": f"'{raw_cell_value}'",
                            "Allowed": "Clean text"
                        })

                    # 2. Content
                    clean_cell_value = raw_cell_value.strip()
                    user_values = [v.strip() for v in clean_cell_value.split('|')]
                    for val in user_values:
                        if not val: continue
                        if val.lower() not in valid_values[m_col]:
                            mistakes.append({
                                "Row": index + 2,
                                "Column": u_col,
                                "Error Type": "Invalid Content",
                                "Invalid Value": val,
                                "Full Cell Content": raw_cell_value,
                                "Allowed": list(valid_values[m_col])[:3]
                            })

            progress_bar.empty()

            if mistakes:
                st.error(f"Found {len(mistakes)} Issues!")
                results_df = pd.DataFrame(mistakes)
                st.dataframe(results_df, use_container_width=True)
            else:
                st.balloons()
                st.success("✅ Amazing! No invalid values or whitespace errors found.")

    # ------------------------------------------
    # TAB 2: NEW IMAGE NAME CHECKER
    # ------------------------------------------
    with tab2:
        st.subheader("🖼️ Image Name vs. Excel Checker")
        st.info("Paste your file paths below. I will clean them (remove folders, convert '_' to '/') and match them against Column A.")

        # 1. Get Excel Names (Try to find 'Glasses name', else take Column A)
        excel_name_col = next((c for c in user_df.columns if "Glasses name" in c), user_df.columns[0])
        excel_names_raw = user_df[excel_name_col].dropna().astype(str).tolist()
        
        # Clean Excel Names (Standardize for comparison)
        excel_names_set = set(n.strip().lower() for n in excel_names_raw if n.strip())
        
        st.write(f"📂 **Excel Column Used:** `{excel_name_col}` ({len(excel_names_set)} unique names)")

        # 2. Paste Area
        pasted_paths = st.text_area("Paste File Paths Here (one per line)", height=300)
        
        if st.button("🔍 Check Images"):
            if not pasted_paths.strip():
                st.warning("Please paste some paths first!")
            else:
                image_report = []
                # Process Paths
                pasted_lines = pasted_paths.split('\n')
                found_images_set = set()
                
                for line in pasted_lines:
                    if not line.strip(): continue
                    
                    # LOGIC:
                    # 1. Get filename: C:\...\Name.png -> Name.png
                    filename = line.split('\\')[-1] 
                    
                    # 2. Remove extension: Name.png -> Name
                    # (rsplit limits it to the last dot, handling dots in names better)
                    if '.' in filename:
                        clean_name = filename.rsplit('.', 1)[0]
                    else:
                        clean_name = filename
                        
                    # 3. Replace '_' with '/'
                    clean_name = clean_name.replace('_', '/')
                    
                    found_images_set.add(clean_name.strip().lower())

                # COMPARISON
                missing_in_images = [n for n in excel_names_set if n not in found_images_set]
                extra_in_images = [n for n in found_images_set if n not in excel_names_set]

                # DISPLAY RESULTS
                col_miss, col_extra = st.columns(2)
                
                with col_miss:
                    st.error(f"❌ Missing Images ({len(missing_in_images)})")
                    st.caption("These names are in Excel but you didn't paste an image for them.")
                    if missing_in_images:
                        st.dataframe(pd.DataFrame(missing_in_images, columns=["Missing Names"]), use_container_width=True)
                    else:
                        st.success("All Excel items have an image!")

                with col_extra:
                    st.warning(f"⚠️ Extra Images ({len(extra_in_images)})")
                    st.caption("These images were pasted but don't match any name in Excel.")
                    if extra_in_images:
                        st.dataframe(pd.DataFrame(extra_in_images, columns=["Orphaned Images"]), use_container_width=True)
                    else:
                        st.success("No extra images found.")
