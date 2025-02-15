import streamlit as st
import pandas as pd
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def add_record_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("➕ নতুন রেকর্ড যোগ করুন")

    db = Database()

    # Get all batches
    batches = db.get_all_batches()

    if not batches:
        st.info("কোন ব্যাচ পাওয়া যায়নি। প্রথমে একটি ব্যাচ তৈরি করুন।")
        return

    # Batch selection
    selected_batch = st.selectbox(
        "ব্যাচ নির্বাচন করুন",
        options=[batch['name'] for batch in batches],
        format_func=lambda x: f"ব্যাচ: {x}"
    )

    # Get selected batch ID
    batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)

    # Get files for selected batch
    files = db.get_batch_files(batch_id)

    if not files:
        st.info("এই ব্যাচে কোন ফাইল নেই। প্রথমে একটি ফাইল আপলোড করুন।")
        return

    # File selection
    selected_file = st.selectbox(
        "ফাইল নির্বাচন করুন",
        options=[file['file_name'] for file in files],
        format_func=lambda x: f"ফাইল: {x}"
    )

    # Form for new record
    with st.form("add_record_form"):
        st.subheader("রেকর্ড তথ্য")

        col1, col2 = st.columns(2)

        with col1:
            si_number = st.text_input("ক্রমিক নং", key="si_number")
            name = st.text_input("নাম", key="name")
            voter_no = st.text_input("ভোটার নং", key="voter_no")
            father_name = st.text_input("পিতার নাম", key="father_name")

        with col2:
            mother_name = st.text_input("মাতার নাম", key="mother_name")
            occupation = st.text_input("পেশা", key="occupation")
            birth_date = st.text_input("জন্ম তারিখ", key="birth_date")
            address = st.text_area("ঠিকানা", key="address")

        # Additional information
        st.subheader("অতিরিক্ত তথ্য")
        phone = st.text_input("ফোন নাম্বার", key="phone")
        facebook = st.text_input("ফেসবুক লিঙ্ক", key="facebook")
        photo = st.text_input("ছবির লিঙ্ক", key="photo")
        description = st.text_area("বিবরণ", key="description")

        # Submit button
        submitted = st.form_submit_button("রেকর্ড যোগ করুন", type="primary")

        if submitted:
            try:
                # Prepare record data
                record_data = {
                    'ক্রমিক_নং': si_number,
                    'নাম': name,
                    'ভোটার_নং': voter_no,
                    'পিতার_নাম': father_name,
                    'মাতার_নাম': mother_name,
                    'পেশা': occupation,
                    'জন্ম_তারিখ': birth_date,
                    'ঠিকানা': address,
                    'phone_number': phone,
                    'facebook_link': facebook,
                    'photo_link': photo,
                    'description': description
                }

                # Add record to database
                db.add_record(batch_id, selected_file, record_data)
                st.success("✅ রেকর্ড সফলভাবে যোগ করা হয়েছে!")

                # Clear form (by rerunning the page)
                st.rerun()

            except Exception as e:
                logger.error(f"Error adding record: {str(e)}")
                st.error(f"রেকর্ড যোগ করার সময় সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    add_record_page()
