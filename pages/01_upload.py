import streamlit as st
import os
from attached_assets.data_processor import process_text_file
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def upload_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("📤 ফাইল আপলোড")

    db = Database()

    # Batch name input
    batch_name = st.text_input("ব্যাচের নাম", placeholder="ব্যাচের নাম লিখুন")

    # File upload
    uploaded_files = st.file_uploader(
        "টেক্সট ফাইল আপলোড করুন",
        type=['txt'],
        accept_multiple_files=True
    )

    if uploaded_files and batch_name:
        if st.button("আপলোড করুন", type="primary"):
            try:
                with st.spinner("প্রক্রিয়াকরণ চলছে..."):
                    # Check if batch already exists
                    existing_batch = db.get_batch_by_name(batch_name)
                    if existing_batch:
                        batch_id = existing_batch['id']
                        st.info(f"'{batch_name}' ব্যাচে ফাইল যোগ করা হচ্ছে...")
                    else:
                        # Create new batch
                        batch_id = db.add_batch(batch_name)
                        st.success(f"নতুন ব্যাচ '{batch_name}' তৈরি করা হয়েছে")

                    total_records = 0
                    for uploaded_file in uploaded_files:
                        content = uploaded_file.read().decode('utf-8')
                        records = process_text_file(content)

                        # Store records in database
                        for record in records:
                            db.add_record(batch_id, uploaded_file.name, record)
                            total_records += 1

                    st.success(f"সফলভাবে {len(uploaded_files)} টি ফাইল এবং {total_records} টি রেকর্ড আপলোড করা হয়েছে!")

            except Exception as e:
                logger.error(f"Upload error: {str(e)}")
                st.error(f"আপলোড ব্যর্থ হয়েছে: {str(e)}")

    # Display existing batches
    st.subheader("বিদ্যমান ব্যাচসমূহ")
    batches = db.get_all_batches()

    if batches:
        for batch in batches:
            with st.expander(f"ব্যাচ: {batch['name']} ({batch['created_at'].strftime('%Y-%m-%d %H:%M')})"):
                records = db.get_batch_records(batch['id'])
                st.write(f"মোট রেকর্ড: {len(records)}")
    else:
        st.info("কোন ব্যাচ পাওয়া যায়নি")

if __name__ == "__main__":
    upload_page()