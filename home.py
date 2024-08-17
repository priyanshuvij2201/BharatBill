import streamlit as st
import upload_bill
import view_inventory

# Define CSS style for centering text horizontally and vertically
centered_style = """
    <style>
    .centered {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        text-align: center;
    }
    </style>
"""

# Streamlit home page layout
def homepage():
    # Apply CSS style for centering text
    st.markdown(centered_style, unsafe_allow_html=True)

    # Set title
    st.title("VyaparTracker")

    # Add some spacing
    st.write("")
    st.write("")
    st.write("")
    st.write("")

    # Description text
    st.markdown("<h3 class='centered'>Experience the most easy Invoice and Inventory Management</h3>", unsafe_allow_html=True)

# Main function to run the Streamlit app
def main():
    # Set the homepage title
    st.title("VyaparTracker")

    # Add buttons for navigation
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Upload Bill"):
            upload_bill.navigate_to_upload_page()

    with col2:
        if st.button("View Inventory"):
            view_inventory.view_seller()

if __name__ == "__main__":
    main()
