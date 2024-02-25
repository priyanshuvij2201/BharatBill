import streamlit as st
import testMod as tm
import products as p

def view_seller():
    conn = tm.connect_database("products.db")
    sellers = tm.display_sellers(conn)
    selected_seller_id = st.session_state.get('selected_seller_id')
    st.write("Select a Seller to view invoices")
    for seller in sellers:
        button_clicked = st.button(f"{seller[1]}")
        if button_clicked:
            st.experimental_set_query_params(selected_seller=seller[0])  # Set the query parameter
            #view_products(seller[0])
            p.view_products(seller[0])

def main():
    view_seller()

if __name__ == "__main__":
    main()
