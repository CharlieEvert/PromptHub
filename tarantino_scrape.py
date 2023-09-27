import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import io
import re
from multiprocessing import Pool, cpu_count
import time

openai.api_key = Nunya

# Function to download, process each PDF, and extract text
def process_pdf(row):
    # De-structure the row into name, year, and pdf_link
    name, year, pdf_link = row
    
    # Initialize DataFrames to store text and errors
    text_df = pd.DataFrame(columns=['Name', 'Year', 'Page', 'Text'])
    error_df = pd.DataFrame(columns=['Name', 'Year', 'PDF_Link', 'Error'])
    
    # Set the request headers to avoid request denial
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.scriptslug.com/scripts/writer/quentin-tarantino"
    }
    
    # Sleep for 5 seconds to avoid rate limiting
    time.sleep(5)
    
    # Send a get request to download the PDF
    pdf_response = requests.get(pdf_link, headers)
    
    # Check if the response is successful
    if pdf_response.status_code == 200:
        # Convert the content to a PDF file
        pdf_file = io.BytesIO(pdf_response.content)
        
        try:
            # Open the PDF and extract text from each page
            with pdfplumber.open(pdf_file) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    # Append the extracted text to the text DataFrame
                    text_df = pd.concat([text_df, pd.DataFrame({
                        'Name': [name],
                        'Year': [year],
                        'Page': [i + 1],
                        'Text': [text]
                    })], ignore_index=True)
        except Exception as e:
            # If any error occurs during PDF processing, log it to the error DataFrame
            error_df = pd.concat([error_df, pd.DataFrame({
                'Name': [name], 
                'Year': [year], 
                'PDF_Link': [pdf_link], 
                'Error': [str(e)]
            })], ignore_index=True)
    else:
        # If PDF download fails, log it to the error DataFrame
        error_df = pd.concat([error_df, pd.DataFrame({
            'Name': [name], 
            'Year': [year], 
            'PDF_Link': [pdf_link], 
            'Error': [f"Failed to download PDF. Status code: {pdf_response.status_code}"]
        })], ignore_index=True)
    
    # Return the DataFrames
    return text_df, error_df

# Function to clean the extracted text
def clean_text(text):
    # Remove multiple special characters
    text = re.sub(r"[!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~]{2,}", ' ', text)
    # Remove single characters
    text = re.sub(r'\b\w\b', ' ', text)
    # Remove extra whitespaces
    return re.sub(r'\s+', ' ', text).strip()

# Main function to scrape the URLs, download, and process the PDFs
def main():
    # Define the URL of the page containing script links
    url = "https://www.scriptslug.com/scripts/writer/quentin-tarantino"
    # Send a get request to the page
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find all script links on the page
        script_links = soup.find_all('a', {'class': 'w-full'})
        
        # Extract name, year, and pdf link for each script
        data = [(link.get('aria-label').split('(')[0].strip(), 
                 link.get('aria-label').split('(')[1].split(')')[0], 
                 link.get('href').replace('https://www.scriptslug.com/script', 'https://assets.scriptslug.com/live/pdf/scripts') + '.pdf') 
                for link in script_links if link.get('aria-label')]
        
        # Use multiprocessing to process PDFs in parallel
        with Pool(cpu_count()) as pool:
            text_dfs, error_dfs = zip(*pool.map(process_pdf, data))
        
        # Concatenate the results into single DataFrames
        text_df = pd.concat(text_dfs, ignore_index=True)
        error_df = pd.concat(error_dfs, ignore_index=True)
        
        # Clean the extracted text
        text_df['Text'] = text_df['Text'].apply(clean_text)
        
        # Return the resulting DataFrames
        return text_df, error_df
    else:
        # Print an error message if the page retrieval fails
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        # Return empty DataFrames
        return pd.DataFrame(columns=['Name', 'Year', 'Page', 'Text']), pd.DataFrame(columns=['Name', 'Year', 'PDF_Link', 'Error'])

# Check if the script is run directly
if __name__ == '__main__':
    # Call the main function and store the results
    result_df, error_df = main()
    # Print the results
    print(result_df)
    print(len(result_df))
    print(error_df)

result_df.to_csv('tarantino_moves.csv')
