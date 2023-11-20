import argparse
import pandas as pd
from openai import OpenAI
import time
from get_endpoint_html import setup_driver, get_page_text
import yagmail

import streamlit as st


class ComplimentGenerator:
    def __init__(self, csv_file, api_key):
        self.csv_file = csv_file

        self.driver = setup_driver()
        self.client = OpenAI(api_key=api_key)
        self.website_column = "site"
        self.modified_prompt = """Using the source text from the business's website: '''{page_text}''', craft a unique and personalized compliment that highlights a specific and distinctive aspect or feature evident in the text. This compliment should reflect an intimate understanding of what sets the business apart, focusing on elements such as a particular product, service, or an aspect of their customer experience, as gleaned from the page text. It should be concise , and serve as an effective segue into the offer of a complimentary website audit. The compliment should feel genuine and be clearly tailored to the unique characteristics of the website, demonstrating that it's coming from someone who has taken the time to understand and appreciate what makes the website special. The goal is to create a compliment that resonates with the specific details and qualities presented in the '''{page_text}'''. focus solely on the compliment itself."""

    def fetch_page_text(self, url):
        return get_page_text(self.driver, url)

    def generate_compliment(self, page_text):
        messages = self.modified_prompt.format(page_text=page_text)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": messages},
            ],
        )

        print(response.choices[0].message.content)
        return response.choices[0].message.content

    def process_websites(self):
        spreadsheet = self.csv_file

        website_links = list(spreadsheet[self.website_column])

        # Initialize a list to store compliments
        compliments = []

        # Loop over each website link and generate a compliment
        for website_link in website_links:
            try:
                page_text = self.fetch_page_text(website_link)
            except:
                page_text = None
            if page_text:
                compliment = self.generate_compliment(page_text)
                compliments.append(compliment)
            else:
                compliments.append(False)

        # Add the compliments as a new column to the dataframe
        spreadsheet["compliment"] = compliments
        return spreadsheet

    def send_results_email(self, dataframe, recipient_email):
        # Convert DataFrame to CSV
        filename = "compliments.csv"
        dataframe.to_csv(filename, index=False)

        # Initialize yagmail
        sender_email = st.secrets["gmail_email"]
        sender_password = st.secrets["gmail_password"]
        yagmail.register(sender_email, sender_password)

        yag = yagmail.SMTP(sender_email)

        # Email subject and body
        subject = "Here's your results for compliment generation"
        body = "Please find attached the compliments generated for your websites."

        # Sending the email
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=body,
            attachments=filename,
        )

        print(f"Email sent successfully to {recipient_email}")
