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

# Upload CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Convert to DataFrame and display
    email = st.text_input("Enter email you want the result file sent to.")
    dataframe = pd.read_csv(uploaded_file)
    st.write(dataframe)
    api_key = st.secrets["openai_api"]
    generator = ComplimentGenerator(dataframe, api_key)

    # Select Website Column
    website_column = st.selectbox(
        "Select the column with website URLs", dataframe.columns
    )

    # Display and Modify Existing Prompt
    existing_prompt = generator.modified_prompt
    modified_prompt = st.text_area("Modify the prompt", value=existing_prompt)
    password = st.text_area("Enter password")

    # Check if {page_text} is still in the modified prompt
    if "{page_text}" not in modified_prompt:
        st.error("Your prompt must contain '{page_text}'")
    # Process and Download Button
    if st.button("Generate Compliments") and password == st.secrets["password"]:
        print(website_column)
        with st.spinner("Wait for it... generating compliments!"):
            updated_csv = run_compliment_generator(
                generator, modified_prompt, website_column
            )
        st.success("Done!")
        st.write("Processing Complete")

        csv = convert_df(updated_csv)
        generator.send_results_email(updated_csv, email)
        st.download_button(
            "Press to Download", csv, "file.csv", "text/csv", key="download-csv"
        )
