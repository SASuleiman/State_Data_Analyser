import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="State Data Separator", layout="centered")
st.title("Excel Data Separator (By State)")

# File uploader
uploaded_file = st.file_uploader("Upload your Excel file (.xlsx)", type=["xlsx", "xls"])

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
            
            # Normalize column names to lowercase to catch "State", "STATE", or "state"
            original_columns = df.columns.tolist()
            df.columns = df.columns.str.strip().str.lower()
            
            if 'state' not in df.columns:
                st.error(f"Column 'state' not found in sheet: '{target_sheet}'. Available columns: {', '.join(original_columns)}")
            else:
                # Restore original column names for the output, but keep a reference to the state column
                state_col_index = df.columns.get_loc('state')
                df.columns = original_columns
                actual_state_col = original_columns[state_col_index]
                
                # Get unique, non-null states
                states = df[actual_state_col].dropna().unique()
                
                st.success(f"Loaded sheet '{target_sheet}'. Found {len(states)} unique states.")
                
                # Dropdown to select a state to view and download
                selected_state = st.selectbox("Select a state to process:", sorted(states))
                
                if selected_state:
                    # Filter data
                    state_df = df[df[actual_state_col] == selected_state]
                    
                    st.write(f"**Previewing {len(state_df)} rows for {selected_state}:**")
                    st.dataframe(state_df.head(10))
                    
                    # Create in-memory Excel file for download
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        # Sheet names are limited to 31 characters in Excel
                        safe_sheet_name = str(selected_state)[:31]
                        state_df.to_excel(writer, index=False, sheet_name=safe_sheet_name)
                    
                    # Download button
                    st.download_button(
                        label=f"Download {selected_state} Data (.xlsx)",
                        data=output.getvalue(),
                        file_name=f"{selected_state}_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )

    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")