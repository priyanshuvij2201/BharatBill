import fitz  # PyMuPDF
import os
import json
import sqlite3
import streamlit as st
from openai import OpenAI
from datetime import datetime

# Environment Setup
def get_api_key():
    api_key = st.secrets["API_KEY"]
    if not api_key:
        raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")
    return api_key

# Database Operations
def connect_database(database_file):
    try:
        conn = sqlite3.connect(database_file)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def initialize_database(conn):
    cursor = conn.cursor()
    # Create Sellers Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sellers (
        SellerID INTEGER PRIMARY KEY AUTOINCREMENT,
        SellerName TEXT UNIQUE NOT NULL
    )''')
    
    # Create Invoices Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Invoices (
        InvoiceID INTEGER PRIMARY KEY AUTOINCREMENT,
        SellerID INTEGER,
        InvoiceNumber TEXT NOT NULL,
        Date TEXT NOT NULL,
        UNIQUE(SellerID, InvoiceNumber),
        FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID)
    )''')
    
    # Create Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        InvoiceID INTEGER,
        ProductName TEXT NOT NULL,
        HSN_SAC INTEGER,
        Amount REAL,
        Rate REAL,
        Quantity INTEGER,
        GST INTEGER,
        Rate_Incl REAL,
        FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID)
    )''')
    
    conn.commit()

def ensure_seller_exists(conn, seller_name):
    cursor = conn.cursor()
    cursor.execute("SELECT SellerID FROM Sellers WHERE SellerName = ?", (seller_name,))
    result = cursor.fetchone()
    if result:
        return result[0]  # Seller already exists, return SellerID
    else:
        cursor.execute("INSERT INTO Sellers (SellerName) VALUES (?)", (seller_name,))
        conn.commit()
        return cursor.lastrowid  # Return the new SellerID

def ensure_invoice_exists(conn, seller_id, invoice_number, date):
    cursor = conn.cursor()
    cursor.execute("SELECT InvoiceID FROM Invoices WHERE SellerID = ? AND InvoiceNumber = ?", (seller_id, invoice_number))
    result = cursor.fetchone()
    if result:
        return result[0], False  # Invoice already exists, return InvoiceID and False
    else:
        cursor.execute("INSERT INTO Invoices (SellerID, InvoiceNumber, Date) VALUES (?, ?, ?)", (seller_id, invoice_number, date))
        conn.commit()
        return cursor.lastrowid, True  # Return the new InvoiceID and True

def insert_product_data(conn, seller_info, invoice_info, products_json):
    seller_id = ensure_seller_exists(conn, seller_info['Seller Name'])
    invoice_id, is_new_invoice = ensure_invoice_exists(conn, seller_id, invoice_info['invoice number'], invoice_info['date'])
    print(seller_info)
    print(invoice_info)
    
    if not is_new_invoice:
        print(f"Invoice {invoice_info['invoice number']} for seller {seller_info['Seller Name']} is already in the database.")
        return
    
    try:
        cursor = conn.cursor()
        for item in products_json:
            print(item)
            cursor.execute('''INSERT INTO Products (InvoiceID, ProductName, HSN_SAC, Amount, Rate, Quantity, GST, Rate_Incl)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (invoice_id, item['Product Name'], item['HSN/SAC'], item['Amount'], item['Rate'], item['Quantity'], item['GST'], item['Rate Incl']))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting product data: {e}")

def create_products_table(conn):
    try:
        cursor = conn.cursor()
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
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def fetch_products(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Products")
        products = cursor.fetchall()
        #for product in products:
            #print(product)
        return products
    except sqlite3.Error as e:
        print(f"Error fetching products: {e}")
    

def display_sellers(conn):
    print("Sellers:")
    cursor = conn.cursor()
    cursor.execute("SELECT SellerID, SellerName FROM Sellers")
    sellers = cursor.fetchall()
    for seller in sellers:
        print(f"ID: {seller[0]}, Name: {seller[1]}")
    print()  # Print a newline for better readability
    return sellers

def display_invoices(conn):
    print("Invoices:")
    cursor = conn.cursor()
    # Assuming the Invoices table includes a reference to SellerID
    cursor.execute("""
        SELECT Invoices.InvoiceID, Invoices.InvoiceNumber, Invoices.Date, Sellers.SellerName 
        FROM Invoices 
        JOIN Sellers ON Invoices.SellerID = Sellers.SellerID
    """)
    invoices = cursor.fetchall()
    # for invoice in invoices:
    #     print(f"ID: {invoice[0]}, Number: {invoice[1]}, Date: {invoice[2]}, Seller: {invoice[3]}")
    # print()
    return invoices  # Print a newline for better readability

# PDF Processing
def read_pdf_text(file_path,startText):
    with fitz.open(file_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    print(startText+"Hello")
# Extract a portion of the text for demonstration
    start = text.find(startText)
    if start != -1:
        sample_text = text[start:start+3000]  # Show the first 1000 characters from where "Sl" is found
        return sample_text

def read_sellerinfo(file_path,startText):
    with fitz.open(file_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
    print(startText)
# Extract a portion of the text for demonstration
    start = text.find(startText)
    if start!= -1:
        extracted_text = text[:start]
        return extracted_text
    else:
        print("The term 'Sl' was not found in the document.")

# API Interaction
def process_text_with_api(api_key, text, prompt):
    client = OpenAI(api_key=api_key)
    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=text + "\n" + prompt,
            temperature=1,
            max_tokens=2650,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        print(response.choices[0].text)
        return response.choices[0].text
    except Exception as e:
        print(f"An error occurred with the API: {e}")
        return None

# Main Workflow
def main():
    database_file = 'products3.db'
    pdf_file = 'Iphone11Rashika.pdf'
    api_key = get_api_key()

    # Database setup
    conn = connect_database(database_file)
    if conn is not None:
        initialize_database(conn)

    seller_info = json.loads(process_text_with_api(api_key, read_sellerinfo(pdf_file), "From the above data find the seller name their state , gstin ,invoice no and date of bill and give it in json format with field stricly as \"Seller Name\",\"State\",\"GSTIN/UIN\",\"Invoice No.\",\"Date of Bill\" " ))

    # date_obj = datetime.strptime(seller_info["Date of Bill"], "%d-%b-%y")
    date_obj=datetime.strptime("01-jul-23", "%d-%b-%y")
    # Format the datetime object into a string in the desired format (ISO 8601)
    formatted_date = date_obj.strftime("%Y-%m-%d")

    sellerDetails = {
    "Seller Name": seller_info["Seller Name"],
    "State": seller_info["State"],
    "GSTIN": seller_info["GSTIN/UIN"]
}

# Extracting invoice_info
    invoice_info = {
        "invoice number": seller_info["Invoice No."],
        "date": formatted_date
    }

    # Read PDF
    text = read_pdf_text(pdf_file)
    if text is not None:
        # Process text for product information
        products_json =process_text_with_api(api_key, text, "Convert the following product data into a structured and JSON format The JSON is an array which should include fields for 'Product Name', 'HSN/SAC', 'Amount', 'Rate', 'Quantity', 'GST', and 'Rate Incl'. Each field's data type and calculation method are as follows: 'Product Name' is a string, 'HSN/SAC' is an int with an 8-digit code, 'Amount' is an int calculated as Rate * Quantity, 'Rate' is the price of the product without taxes, 'Quantity' is the number of products, 'GST' is the Goods and Services Tax in percentage, and 'Rate Incl' is the rate including GST percentage Please ensure the JSON output does not use anything as indices and follows the format strictly Return only the json structure and nothing else ")
        print("hello"+products_json)
        products_json=json.loads(products_json)
        if products_json:
            insert_product_data(conn, sellerDetails, invoice_info, products_json)
    #     print(products_json)

        # Process text for seller information
    # Fetch and display products from the database
    if conn is not None:
        display_sellers(conn)
        display_invoices(conn)
        fetch_products(conn)
        conn.close()

if __name__ == "__main__":
    main()
