import streamlit as st
import pandas as pd
import io

# Set up the page
st.set_page_config(page_title="State Data Separator", page_icon="🗺️", layout="wide")
st.title("🗺️ Excel Data Separator (By State)")

# 1. Quick Explanation
st.markdown("""
**What this tool does:** It reads an uploaded Excel file, targets the second sheet, and groups the data by the `state` column. It provides a visual breakdown and allows you to download isolated data for any specific state.
""")

with st.expander("Need help formatting your Excel file?"):
    st.markdown("""
    1. Ensure your file is an **.xlsx** or **.xls** format.
    2. The data you want to separate must be on the **second sheet** (the script ignores the first sheet).
    3. Ensure there is a column explicitly named **State** (case-insensitive).
    """)

st.divider()

# Sidebar Setup
st.sidebar.header("⚙️ Controls")
if st.sidebar.button("🔄 Refresh Dashboard", help="Click to reload the application."):
    st.rerun()

st.sidebar.divider()

# Main Area Upload
st.subheader("1. Upload Data")
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx", "xls"])

st.divider()

if uploaded_file is not None:
    try:
        # Load the Excel file
        xls = pd.ExcelFile(uploaded_file)
        
        # Ensure there is a second sheet
        if len(xls.sheet_names) < 2:
            st.error("The uploaded file does not contain a second sheet.")
        else:
            # Target the second sheet (index 1)
            target_sheet = xls.sheet_names[1]
            df = pd.read_excel(xls, sheet_name=target_sheet)
            
            # Normalize column names to catch variations of "State"
            original_columns = df.columns.tolist()
            df.columns = df.columns.str.strip().str.lower()
            
            if 'state' not in df.columns:
                st.error(f"Column 'state' not found in sheet: '{target_sheet}'. Available columns: {', '.join(original_columns)}")
            else:
                # Restore original column names for output, keep reference to the state column
                state_col_index = df.columns.get_loc('state')
                df.columns = original_columns
                actual_state_col = original_columns[state_col_index]
                
                # Clean and get states
                df[actual_state_col] = df[actual_state_col].fillna('Unknown')
                states = sorted(df[actual_state_col].astype(str).unique())
                
                # --- METRICS DASHBOARD ---
                st.subheader("📊 Dataset Overview")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Rows Processed", len(df))
                col2.metric("Unique States Found", len(states))
                col3.metric("Target Sheet Name", target_sheet)
                
                st.divider()
                
                # --- VISUAL ANALYTICS & FILTERING ---
                col_chart, col_filter = st.columns([1, 1])
                
                with col_chart:
                    st.subheader("📈 Record Distribution by State")
                    state_counts = df[actual_state_col].value_counts().head(15)
                    st.bar_chart(state_counts)
                
                with col_filter:
                    st.subheader("🔍 Extract State Data")
                    selected_state = st.selectbox("Select a state to view and download:", states)
                    
                    if selected_state:
                        state_df = df[df[actual_state_col] == selected_state]
                        st.info(f"**{selected_state}** has **{len(state_df)}** records.")
                        
                        # Create in-memory Excel file for download
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            safe_sheet_name = str(selected_state)[:31]
                            state_df.to_excel(writer, index=False, sheet_name=safe_sheet_name)
                        
                        # Download button
                        st.download_button(
                            label=f"📥 Download {selected_state} Data (.xlsx)",
                            data=output.getvalue(),
                            file_name=f"{selected_state}_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            use_container_width=True
                        )

                # --- DATA PREVIEW ---
                st.divider()
                st.subheader(f"📋 Data Preview: {selected_state}")
                st.dataframe(state_df, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while processing the file. Details: {str(e)}")