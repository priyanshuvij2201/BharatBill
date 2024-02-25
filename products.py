import streamlit as st
import testMod as tm
import pandas as pd

def view_products(selected_seller_id):
    st.write("Invoices of the selected seller")
    conn = tm.connect_database("products.db")
    
    # Fetch all invoices of the selected seller
    invoices = conn.execute(f"SELECT InvoiceNumber FROM Invoices WHERE SellerId={selected_seller_id}")
    invoice_numbers = [i[0] for i in invoices]
    
    # Display selectbox to choose an invoice
    selected_option = st.selectbox("Select Invoice for viewing products", invoice_numbers)
    
    # Button to view products
    if selected_option:  # If an invoice is selected
        invoice_id = conn.execute(f"SELECT InvoiceID FROM Invoices WHERE InvoiceNumber='{selected_option}'").fetchone()[0]
        products = conn.execute(f"SELECT ProductName, HSN_SAC, Amount, Rate, Quantity, GST, Rate_Incl FROM Products WHERE InvoiceID={invoice_id}")
        
        # Display the table with column names
        st.write("Products")
        column_names = ['Product Name', 'HSN/SAC', 'Amount', 'Rate', 'Quantity', 'GST', 'Rate Incl']
        df = pd.DataFrame(products, columns=column_names)
        st.write(df)


