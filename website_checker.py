import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# Function to check website availability
def check_website(url):
    try:
        response = requests.get(url, timeout=10)
        # Return True if status code is an error (4xx or 5xx)
        return url, response.status_code >= 400
    except requests.exceptions.RequestException:
        # Return True if there is any exception (e.g., connection error)
        return url, True


# Read the Excel file
input_excel_file = "website_csv.csv"  # Replace with your input file path
df = pd.read_csv(input_excel_file)

# Create a ThreadPoolExecutor to parallelize the task
with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers as needed
    future_to_url = {executor.submit(check_website, url): url for url in df["site"]}
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            _, has_error = future.result()
            df.loc[df["site"] == url, "has_error"] = has_error
        except Exception as exc:
            print(f"{url} generated an exception: {exc}")

# Filter the DataFrame to keep only rows with errors
error_websites_df = df[df["has_error"]]

# Save the filtered DataFrame to a new Excel file
output_excel_file = "output_website.csv"  # Replace with your desired output file path
error_websites_df.to_csv(output_excel_file)

print("Filtered DataFrame saved to", output_excel_file)
