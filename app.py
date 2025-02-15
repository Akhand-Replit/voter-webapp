import os
import sys
import streamlit as st
import logging
import pandas as pd

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from attached_assets.auth import init_auth, login_form, logout
from utils.styling import apply_custom_styling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Akhand Data",
    page_icon="📊",
    layout="centered"
)

# Apply custom styling
apply_custom_styling()

# Hide Logos watermark of streamli+github
hide_st_style = """
<style>
._profileContainer_gzau3_53 {visibility: hidden!important;}
._link_gzau3_10  {visibility: hidden!important;}
.st-emotion-cache-15wzwg4 .e1d5ycv517  {visibility: hidden!important;}
.st-emotion-cache-q16mip .e1i26tt71  {visibility: hidden!important;}

</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Initialize authentication
init_auth()

def get_batch_statistics():
    # Placeholder function - replace with actual database query
    return {
        "total_batches": 5,
        "total_files": 1250,
        "recent_batch": "ব্যাচ-২০২৫",
        "processed_data": 1150
    }

def display_profile_card(data):
    with st.container():
        # Profile section with image and basic info
        cols = st.columns([1, 3])

        with cols[0]:
            # Profile image
            st.image("https://placekitten.com/100/100", width=100)

        with cols[1]:
            st.markdown("### বিস্তৃতি")

        # Main information grid
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **ক্রমিক নং:** {data.get('serial_no', '')}\n
            **রেকর্ড নং:** {data.get('record_no', '')}\n
            **পিতার নাম:** {data.get('father_name', '')}\n
            **মাতার নাম:** {data.get('mother_name', '')}\n
            **পেশা:** {data.get('occupation', '')}\n
            **ঠিকানা:** {data.get('address', '')}
            """)

        with col2:
            st.markdown(f"""
            **ফোন নাম্বার:** {data.get('phone', '')}\n
            **ফেসবুক:**""")
            if data.get('facebook_url'):
                st.markdown(f"[{data.get('facebook_url', '')}]({data.get('facebook_url', '')})")
            st.markdown("**বিবরণ:**")


def main():
    # Show logout button if authenticated
    if st.session_state.authenticated:
        # Header section with logout button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("লগ আউট", type="secondary"):
                logout()
                st.rerun()

        with col1:
            st.title("Akhand Data")

        # Description section
        st.markdown("""
        ### সিস্টেম বর্ণনা
        এই ডাটা ম্যানেজমেন্ট সিস্টেমটি বাংলা টেক্সট প্রসেসিং এবং ডাটা বিশ্লেষণের জন্য একটি সমন্বিত প্ল্যাটফর্ম। 
        এটি মাল্টিলিঙ্গুয়াল সম্পর্ক ট্র্যাকিং, উন্নত সার্চ এবং ফিল্টারিং সুবিধা প্রদান করে।
        """)

       
        # User Guide
        st.markdown("""
        ### ব্যবহার নির্দেশিকা

        ১. **ডাটা আপলোড**
        - 📤 "আপলোড পেজ" এ ক্লিক করুন
        - ফাইল নির্বাচন করুন
        - "আপলোড" বাটনে ক্লিক করুন

        ২. **ডাটা অনুসন্ধান**
        - 🔍 "সার্চ পেজ" এ যান
        - অনুসন্ধান ফিল্টার ব্যবহার করুন
        - ফলাফল দেখুন

        ৩. **ডাটা বিশ্লেষণ**
        - 📊 "বিশ্লেষণ" ট্যাবে যান
        - রিপোর্ট জেনারেট করুন
        - স্ট্যাটিসটিক্স দেখুন
        """)

   

        # Main Menu
        st.markdown("### মূল মেনু")
        menu_col1, menu_col2 = st.columns(2)

        with menu_col1:
            st.markdown("""
            - 📤 **আপলোড পেজ**: নতুন ফাইল আপলোড করুন
            - 🔍 **সার্চ পেজ**: তথ্য খুঁজুন
            """)

        with menu_col2:
            st.markdown("""
            - 📁 **সব তথ্য**: সকল সংরক্ষিত তথ্য দেখুন
            - 📊 **বিশ্লেষণ**: ডাটা বিশ্লেষণ দেখুন
            """)

    else:
        login_form()

if __name__ == "__main__":
    main()
