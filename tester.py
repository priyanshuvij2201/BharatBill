from openai import OpenAI
import fitz  # PyMuPDF
import os
import json 
import sqlite3

def fetch_products(database_file):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database_file)
        cursor = conn.cursor()
        
        # Fetch all products from the database
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        print(products)
        # Display the fetched products
    except sqlite3.Error as e:
        print("Error fetching products:", e)
    
    finally:
        # Close the database connection
        if conn:
            conn.close()

# Ensure you have set your API key in an environment variable for better security
api_key = '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'
if not api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

# Open the PDF file
with fitz.open("kp.pdf") as pdf:
    text = ""
    for page in pdf:
        text += page.get_text()

# Extract a portion of the text for demonstration
start = text.find('Sl')
if start != -1:
    sample_text = text[start:start+3000]  # Show the first 1000 characters from where "Sl" is found
    print(sample_text)
else:
    print("The term 'Sl' was not found in the document.")

if start!= -1:
    extracted_text = text[:start]
    print(extracted_text)
else:
    print("The term 'Sl' was not found in the document.")

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=api_key)

# Use a meaningful prompt based on your application's needs
prompt = "format the text in a tabular format starting from SL and then  convert it strctlly in json format with fields Product Name: String , HSN/SAC: int ,Amount:int , Rate : int,Quantity: intGST : int ,Rate Incl : int}"

try:
    response = client.completions.create(
      model="gpt-3.5-turbo-instruct",
      prompt=sample_text+"\n"+prompt,  # Combine the prompt with the extracted text
      temperature=1,
      max_tokens=3000,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0,
    )
except Exception as e:
    print(f"An error occurred: {e}")



api_text=response.choices[0].text
products_json = json.loads(api_text)
print(products_json)

def fetch_details(extracted_text):
    prompt = "From the above data find the seller name their state , gstin ,invoice no and date of bill and give it in json format "

    try:
        response = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=extracted_text+"\n"+prompt,  # Combine the prompt with the extracted text
        temperature=1,
        max_tokens=3000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        )
    except Exception as e:
        print(f"An error occurred: {e}")



    api_text=response.choices[0].text
    details_json = json.loads(api_text)
    print(details_json)
    return details_json



conn = sqlite3.connect('products1.db')
cursor = conn.cursor()

# Create a table to store the product data
cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    ProductName TEXT,
                    HSN_SAC INTEGER,
                    Amount REAL,
                    Rate REAL,
                    Quantity INTEGER,
                    GST INTEGER,
                    Rate_Incl REAL
                  )''')

# Insert data into the table
for item in products_json:
    cursor.execute('''INSERT INTO products (ProductName, HSN_SAC, Amount, Rate, Quantity, GST, Rate_Incl)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (item['Product Name'], item['HSN/SAC'], item['Amount'], item['Rate'], item['Quantity'], item['GST'], item['Rate Incl']))

# Commit changes and close connection
conn.commit()
cursor=conn.execute("select * from products")
for i in cursor:
    print(i)
seller_info=fetch_details(extracted_text)
combined_data = {
    "Seller Info": seller_info,
    "Products": products_json
}

# Convert combined_data to JSON string
combined_json = json.dumps(combined_data, indent=4)

# Print the combined JSON
print(combined_json)
