import streamlit as st
import testMod as tm

def view_products(seller_id):
    if seller_id:
        conn = tm.connect_database("products.db")
        invoices = tm.display_invoices(conn)
        st.write("Invoices for the selected seller are:")
        for invoice in invoices:
            if invoice[0] == seller_id:
                button_clicked = st.button(invoice[1])
                if button_clicked:
                    print("yew we did it ")
                    st.session_state.selected_invoice_id = invoice[0]

def view_seller():
    conn = tm.connect_database("products.db")
    sellers = tm.display_sellers(conn)
    selected_seller_id = st.session_state.get('selected_seller_id')
    for seller in sellers:
        button_clicked = st.button(f"Seller: {seller[1]}")
        if button_clicked:
            st.session_state.selected_seller_id = seller[0]
            view_products(seller[0])

def main():
    view_seller()
    if "selected_invoice_id" in st.session_state:
        st.write(f"Selected invoice ID: {st.session_state.selected_invoice_id}")

if __name__ == "__main__":
    main()
