import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def analysis_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("📊 ডাটা বিশ্লেষণ")

    db = Database()

    try:
        # Get all batches
        batches = db.get_all_batches()

        if not batches:
            st.info("বিশ্লেষণের জন্য কোন ডাটা পাওয়া যায়নি")
            return

        # Batch selection
        selected_batch = st.selectbox(
            "ব্যাচ নির্বাচন করুন",
            options=['সব ব্যাচ'] + [batch['name'] for batch in batches],
            format_func=lambda x: x
        )

        # Total records metrics
        total_metrics_col1, total_metrics_col2 = st.columns(2)

        with total_metrics_col1:
            # Overall statistics
            if selected_batch == 'সব ব্যাচ':
                total_records = sum(len(db.get_batch_records(batch['id'])) for batch in batches)
                st.metric("মোট রেকর্ড (সব ব্যাচ)", total_records)
            else:
                batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)
                batch_records = db.get_batch_records(batch_id)
                st.metric(f"মোট রেকর্ড ({selected_batch})", len(batch_records))

        # Get occupation statistics based on selection
        if selected_batch == 'সব ব্যাচ':
            occupation_stats = db.get_occupation_stats()
        else:
            batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)
            occupation_stats = db.get_batch_occupation_stats(batch_id)

        if occupation_stats:
            # Convert to DataFrame for visualization
            df = pd.DataFrame(occupation_stats)

            # Occupation distribution
            st.subheader("পেশা অনুযায়ী বিতরণ")

            # Create donut chart
            fig = px.pie(
                df,
                values='count',
                names='পেশা',
                title=f"পেশা অনুযায়ী বিতরণ ({selected_batch})",
                hole=0.3
            )
            fig.update_layout(
                font=dict(family="Noto Sans Bengali"),
                height=500,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

            # Batch-wise bar chart
            if selected_batch == 'সব ব্যাচ':
                st.subheader("ব্যাচ অনুযায়ী রেকর্ড বিতরণ")
                batch_stats = []
                for batch in batches:
                    records = db.get_batch_records(batch['id'])
                    batch_stats.append({
                        'ব্যাচ': batch['name'],
                        'রেকর্ড': len(records)
                    })

                batch_df = pd.DataFrame(batch_stats)
                fig_bar = px.bar(
                    batch_df,
                    x='ব্যাচ',
                    y='রেকর্ড',
                    title="ব্যাচ অনুযায়ী মোট রেকর্ড"
                )
                fig_bar.update_layout(
                    font=dict(family="Noto Sans Bengali"),
                    height=400
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # Display detailed table
            st.subheader("বিস্তারিত তথ্য")
            df_display = df.copy()
            df_display.columns = ['পেশা', 'সংখ্যা']
            df_display = df_display.sort_values('সংখ্যা', ascending=False)
            st.dataframe(
                df_display,
                hide_index=True,
                use_container_width=True
            )

        else:
            st.info("বিশ্লেষণের জন্য কোন ডাটা পাওয়া যায়নি")

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        st.error(f"বিশ্লেষণে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    analysis_page()