import re
import pandas as pd
import asyncio
import aiohttp
import nest_asyncio
import time

key = 'nunya'

# Apply the nest_asyncio to solve RuntimeError
nest_asyncio.apply()

# Read the CSV file into a DataFrame
df = pd.read_csv('/Users/charlieevert/Desktop/ai_projects/structured_data_querying/tarantino/tarantino_moves.csv')

# Define the function to clean the text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'([!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~])\1+', r'\1', text)
    text = re.sub(r'\b([^a])\b', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    return text

# Define the asynchronous function to generate embeddings
async def generate_embeddings(session, text):
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    data = {
        "input": text,
        "model": "text-embedding-ada-002"
    }
    
    async with session.post(url, headers=headers, json=data) as response:
        if response.status == 200:
            json_response = await response.json()
            embedding = json_response['data'][0]['embedding']
            total_tokens = json_response['usage']['total_tokens']
            return embedding, total_tokens
        else:
            return None, None

# Define the main asynchronous function
async def main():
    # Clean the 'Text' field in the DataFrame
    df['Text'] = df['Text'].apply(clean_text)
    
    # Start the timer
    start_time = time.time()

    # Initialize the aiohttp session
    async with aiohttp.ClientSession() as session:
        # Use asyncio.gather to run asynchronous tasks concurrently
        tasks = [generate_embeddings(session, text) for text in df['Text']]
        results = await asyncio.gather(*tasks)

    # Append the embeddings and total tokens to the DataFrame
    df['Embedding'], df['Total_Tokens'] = zip(*results)
    
    # Calculate the cost based on total tokens and rate
    rate = 0.0001 / 1000  # Cost per token
    df['Cost'] = df['Total_Tokens'] * rate
    total_cost = df['Cost'].sum()
    
    # Calculate the elapsed time and print it
    elapsed_time = time.time() - start_time
    print(f"Elapsed time: {elapsed_time//60:.0f} minutes {elapsed_time%60:.2f} seconds")
    print(f"Total cost: ${total_cost:.4f}")
    
    # Display the DataFrame
    print(df)
    df.to_excel('tarantino_embeddings.xlsx')
    df.to_csv('tarantino_embeddings.csv')

# Run the main asynchronous function
asyncio.run(main())


