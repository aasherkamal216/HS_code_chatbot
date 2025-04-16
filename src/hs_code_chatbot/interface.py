import re
import pandas as pd

from chatbot import get_chatbot_response, SYSTEM_PROMPT

import streamlit as st

st.set_page_config(page_title="HS Code Assistant")

# Initialize session state (without system message in messages)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to load and cache the Excel file
@st.cache_data
def load_excel_data(filepath):
    try:
        df = pd.read_excel(filepath)
        return df
    except FileNotFoundError:
        st.error(f"Excel file not found at {filepath}.")
        return None

# Load the Excel file with caching
excel_filepath = "HS_CODES_TABLE.xlsx"
df = load_excel_data(excel_filepath)

if df is None:
    st.stop() # Stops execution if the excel file is not found.

# --- Streamlit UI ---
st.title(":blue[HS Code] Assistant")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to extract 10-digit HS code from text (flexible pattern)
def extract_hs_code(text):
    # Matches formats like: 8471.30.10.00, 8471.300000, 8471300000, etc.
    match = re.search(r'\b\d{4}\.?\d{2}\.?\d{2}\.?\d{2}|\d{4}\.?\d{2}\.?\d{4}\b', text)
    return match.group(0) if match else None

# Chat input
if prompt := st.chat_input("What is the HS code for...?"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        response = st.write_stream(
            get_chatbot_response(st.session_state.messages)
        )

    # Extract HS code from the response, if present
    hs_code = extract_hs_code(response)
    if hs_code:

        # Process the HS code and check against the Excel file
        hs_code_processed = "".join(filter(str.isdigit, hs_code)) # remove dots.

        # Filter 8 digit rows and create the combined code.
        df_8digit = df[df['FRACCIÓN ARANCELARIA'].astype(str).str.len() >= 8].copy()

        def combine_code(row):
            hs_part = "".join(filter(str.isdigit, str(row['FRACCIÓN ARANCELARIA'])))
            nico_part = str(row['NICO']).zfill(2) if pd.notna(row['NICO']) else "00"
            return hs_part + nico_part

        df_8digit['COMBINED_CODE'] = df_8digit.apply(combine_code, axis=1)

        if hs_code_processed in df_8digit['COMBINED_CODE'].values:
            st.success("Hs code is correct and is available in the catalog.")
        else:
            st.warning("HS code not found in the catalog!")

    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})