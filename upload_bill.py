import streamlit as st
import testMod as tm
import json
import tempfile
import os
import pandas as pd

def navigate_to_upload_page():
    startText = st.text_input("Enter Text as mentioned in the sample")
    uploaded_file = st.file_uploader("Upload your bill (PDF)", type="pdf")
    products_json=None
    if uploaded_file is not None:
        # Save the uploaded file to a temporary directory
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            file_path = tmp_file.name  # Get the file path of the temporary file
        
        st.write("File uploaded successfully!")

        # Perform further processing as needed
        if st.button("Upload"):
            database_file = 'products.db'
            pdf_file = file_path  # Use the temporary file path
            api_key = tm.get_api_key()

            # Database setup
            conn = tm.connect_database(database_file)
            if conn is not None:
                tm.initialize_database(conn)

            seller_info = json.loads(tm.process_text_with_api(api_key, tm.read_sellerinfo(pdf_file, startText), "From the above data find the seller name their state , gstin ,invoice no and date of bill and give it in json format with field stricly as \"Seller Name\",\"State\",\"GSTIN/UIN\",\"Invoice No.\",\"Date of Bill\" " ))
            try:
                date_obj = tm.datetime.strptime(seller_info["Date of Bill"], "%d-%b-%y")
                # Format the datetime object into a string in the desired format (ISO 8601)
                formatted_date = date_obj.strftime("%Y-%m-%d")
            except Exception as e:
                date_obj = tm.datetime.strptime("03-Jul-23", "%d-%b-%y")
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
            text = tm.read_pdf_text(pdf_file, startText)
            if text is not None:
                # Process text for product information
                products_json = tm.process_text_with_api(api_key, text, "Convert the following product data into a structured and JSON format The JSON is an array which should include fields for 'Product Name', 'HSN/SAC', 'Amount', 'Rate', 'Quantity', 'GST', and 'Rate Incl'. Each field's data type and calculation method are as follows: 'Product Name' is a string, 'HSN/SAC' is an int with an 8-digit code, 'Amount' is an int calculated as Rate * Quantity, 'Rate' is the price of the product without taxes, 'Quantity' is the number of products, 'GST' is the Goods and Services Tax in percentage, and 'Rate Incl' is the rate including GST percentage Please ensure the JSON output does not use anything as indices and follows the format strictly")
                products_json = json.loads(products_json)
                if products_json:
                    tm.insert_product_data(conn, sellerDetails, invoice_info, products_json)

            # Close the database connection
            if conn is not None:
                conn.close()

            # IMPORTANT: Delete the temporary file
            os.remove(file_path)
            json_str = json.dumps(products_json, indent=4)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="uploaded_file.json",
                mime="application/json"
            )
            df = pd.DataFrame(products_json)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="uploaded_file.csv",
                mime="text/csv"
            )

# Call the function to run the Streamlit app
if __name__ == "__main__":
    navigate_to_upload_page()
