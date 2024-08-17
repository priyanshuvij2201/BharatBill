import streamlit as st
import upload_bill
import view_inventory

# Create an instance of the login authentication UI
# __login__obj = __login__(
#     auth_token="pk_prod_03KD363E3G4QBMQ8QCM1CS8VN8WB", 
#     company_name="VyaparTracker",
#     width=200, 
#     height=250, 
#     logout_button_name='Logout', 
#     hide_menu_bool=False, 
#     hide_footer_bool=False, 
#     lottie_url='https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json'
# )

# # Build the login UI and check if the user is logged in
# LOGGED_IN = __login__obj.build_login_ui()

# # If user is logged in, display the rest of the application
# if LOGGED_IN == True:

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
    #homepage()
    main_page_sidebar,selected_option=nav_sidebar()
    if selected_option=="Upload Bill":
        upload_bill.navigate_to_upload_page()
    if selected_option=="View Inventory":
        view_inventory.view_seller()


if __name__ == "__main__":
    main()
