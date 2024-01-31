import streamlit as st
import pandas as pd
from io import StringIO
from email_complimentor import ComplimentGenerator  # Import your existing script


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def run_compliment_generator(generator, modified_prompt, website_column):
    generator.modified_prompt = (
        modified_prompt  # Modify your script to accept a modified prompt
    )
    generator.website_column = str(
        website_column  # Modify your script to use this column for URLs
    )
    csv_file = generator.process_websites()
    return csv_file


st.title("Compliment Generator for Websites")
if "generated_file" not in st.session_state:
    st.session_state.generated_file = None


# Upload CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Convert to DataFrame and display
    email = st.text_input(
        "Enter email you want the result file sent to. Don't use school emails."
    )
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)
    api_key = st.secrets["openai_api"]
    generator = ComplimentGenerator(dataframe, api_key)

    # Select Website Column
    website_column = st.selectbox(
        "Select the column with website URLs", dataframe.columns
    )
    modified_prompt = generator.modified_prompt
    # Display and Modify Existing Prompt
    # existing_prompt = generator.modified_prompt
    # modified_prompt = st.text_area("Modify the prompt", value=existing_prompt)
    password = st.text_input("Enter password")

    # Check if {page_text} is still in the modified prompt
    if "{page_text}" not in modified_prompt:
        st.error("Your prompt must contain '{page_text}'")
    # Process and Download Button
if st.button("Generate Compliments") and password == st.secrets["password"]:
    with st.spinner("Wait for it... generating compliments!"):
        updated_csv = run_compliment_generator(
            generator, modified_prompt, website_column
        )
    st.session_state.generated_file = convert_df(updated_csv)
    st.success("Done!")
    # generator.send_results_email(updated_csv, email)
    # generator.send_results_email(updated_csv, "ayush@science.org.in")

# Download Button - only if file is generated
if st.session_state.generated_file is not None:
    st.write("Processing Complete")
    st.download_button(
        "Press to Download",
        st.session_state.generated_file,
        "file.csv",
        "text/csv",
        key="download-csv",
    )
