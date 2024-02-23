import streamlit as st
import testMod as tm
import json

def navigate_to_upload_page():
    uploaded_file = st.file_uploader("Upload your bill (PDF)", type="pdf")
    if uploaded_file is not None:
        # Process the uploaded file
        st.write("File uploaded successfully!")
        # Perform further processing as needed
        if st.button("Upload"):
            database_file = 'products.db'
            pdf_file = uploaded_file
            api_key = tm.get_api_key()

            # Database setup
            conn = tm.connect_database(database_file)
            if conn is not None:
                tm.initialize_database(conn)

            seller_info = json.loads(tm.process_text_with_api(api_key, tm.read_sellerinfo(pdf_file), "From the above data find the seller name their state , gstin ,invoice no and date of bill and give it in json format with field stricly as \"Seller Name\",\"State\",\"GSTIN/UIN\",\"Invoice No.\",\"Date of Bill\" " ))

            # date_obj = datetime.strptime(seller_info["Date of Bill"], "%d-%b-%y")
            date_obj=tm.datetime.strptime("01-jul-23", "%d-%b-%y")
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
            text = tm.read_pdf_text(pdf_file)
            if text is not None:
                # Process text for product information
                products_json = tm.process_text_with_api(api_key, text, "Convert the following product data into a structured and JSON format The JSON is an array which should include fields for 'Product Name', 'HSN/SAC', 'Amount', 'Rate', 'Quantity', 'GST', and 'Rate Incl'. Each field's data type and calculation method are as follows: 'Product Name' is a string, 'HSN/SAC' is an int with an 8-digit code, 'Amount' is an int calculated as Rate * Quantity, 'Rate' is the price of the product without taxes, 'Quantity' is the number of products, 'GST' is the Goods and Services Tax in percentage, and 'Rate Incl' is the rate including GST percentage Please ensure the JSON output does not use anything as indices and follows the format strictly")
                #print("hello"+products_json)
                products_json=json.loads(products_json)
                if products_json:
                    tm.insert_product_data(conn, sellerDetails, invoice_info, products_json)
            #     print(products_json)

                # Process text for seller information
            
            # Fetch and display products from the database
            if conn is not None:
                #tm.display_sellers(conn)
                #tm.display_invoices(conn)
                #tm.fetch_products(conn)
                conn.close()
