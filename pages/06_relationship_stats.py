import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import Database
from utils.styling import apply_custom_styling
import logging

logger = logging.getLogger(__name__)
apply_custom_styling()

def get_relationship_stats(db, batch_id=None):
    """Get statistics for all relationship statuses"""
    with db.conn.cursor() as cur:
        query = """
            SELECT relationship_status, COUNT(*) as count
            FROM records
            """
        if batch_id:
            query += " WHERE batch_id = %s"
            params = (batch_id,)
        else:
            params = ()

        query += """
            GROUP BY relationship_status
            ORDER BY count DESC
        """
        cur.execute(query, params)
        return cur.fetchall()

def get_batch_relationship_stats(db, selected_batch_id=None):
    """Get relationship statistics per batch"""
    with db.conn.cursor() as cur:
        query = """
            SELECT b.name as batch_name, r.relationship_status, COUNT(*) as count
            FROM records r
            JOIN batches b ON r.batch_id = b.id
            """
        if selected_batch_id:
            query += " WHERE r.batch_id = %s"
            params = (selected_batch_id,)
        else:
            params = ()

        query += """
            GROUP BY b.name, r.relationship_status
            ORDER BY b.name, r.relationship_status
        """
        cur.execute(query, params)
        return cur.fetchall()

def relationship_stats_page():
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.warning("অনুগ্রহ করে প্রথমে লগইন করুন")
        return

    st.title("📁 সারসংক্ষেপ")

    db = Database()

    # Get all batches
    batches = db.get_all_batches()

    if not batches:
        st.info("কোন ডাটা পাওয়া যায়নি")
        return

    # Batch selection
    selected_batch = st.selectbox(
        "ব্যাচ নির্বাচন করুন",
        options=['সব ব্যাচ'] + [batch['name'] for batch in batches],
        format_func=lambda x: f"ব্যাচ: {x}"
    )

    # Get selected batch ID
    selected_batch_id = None
    if selected_batch != 'সব ব্যাচ':
        selected_batch_id = next(batch['id'] for batch in batches if batch['name'] == selected_batch)

    # Get overall statistics based on selection
    stats = get_relationship_stats(db, selected_batch_id)
    if not stats:
        st.info("কোন পরিসংখ্যান পাওয়া যায়নি")
        return

    # Create DataFrame for overall stats
    df_stats = pd.DataFrame(stats, columns=['relationship_status', 'count'])

    # Show total counts at the top
    total_records = df_stats['count'].sum()
    processed_records = df_stats[df_stats['relationship_status'] != 'Regular']['count'].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("মোট", total_records)
    with col2:
        st.metric("নিষ্পত্তি", processed_records)

    # Add pie chart for overall distribution
    st.subheader("🥧 সম্পর্কের ধরণ অনুযায়ী বিতরণ")
    fig_pie = px.pie(
        df_stats,
        values='count',
        names='relationship_status',
        color='relationship_status',
        color_discrete_map={
            'Regular': '#98D8C6',     # Mint color
            'Connected': '#FFF59D',   # Light yellow
            'Friend': '#2ecc71',      # Green
            'Enemy': '#e74c3c'        # Red
        }
    )
    fig_pie.update_layout(
        showlegend=True,
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # Display bar chart for batch-wise distribution
    batch_stats = get_batch_relationship_stats(db, selected_batch_id)
    if batch_stats:
        st.subheader("📊 ব্যাচ অনুযায়ী সম্পর্কের বিতরণ")
        df_batch_stats = pd.DataFrame(batch_stats, columns=['batch_name', 'relationship_status', 'count'])

        # Create bar chart with custom colors
        fig = px.bar(
            df_batch_stats,
            x='batch_name',
            y='count',
            color='relationship_status',
            title='ব্যাচ অনুযায়ী সম্পর্কের বিতরণ',
            color_discrete_map={
                'Regular': '#98D8C6',     # Mint color
                'Connected': '#FFF59D',   # Light yellow
                'Friend': '#2ecc71',      # Green
                'Enemy': '#e74c3c'        # Red
            },
            barmode='group'
        )

        fig.update_layout(
            xaxis_title="ব্যাচের নাম",
            yaxis_title="সংখ্যা",
            legend_title="সম্পর্কের ধরণ",
            plot_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Create detailed statistics table
        st.subheader("📋 বিস্তারিত পরিসংখ্যান")
        pivot_table = df_batch_stats.pivot(
            index='batch_name',
            columns='relationship_status',
            values='count'
        ).fillna(0).astype(int)

        # Ensure all columns exist
        for col in ['Regular', 'Connected', 'Friend', 'Enemy']:
            if col not in pivot_table.columns:
                pivot_table[col] = 0

        pivot_table['মোট'] = pivot_table.sum(axis=1)

        # Reorder columns
        pivot_table = pivot_table[['Regular', 'Connected', 'Friend', 'Enemy', 'মোট']]
        st.dataframe(pivot_table, use_container_width=True)

        # Friend and Enemy specific analysis
        st.subheader("👥 বন্ধু এবং শত্রু বিশ্লেষণ")

        # Filter for Friend and Enemy
        friend_enemy_df = df_batch_stats[df_batch_stats['relationship_status'].isin(['Friend', 'Enemy'])]

        if not friend_enemy_df.empty:
            fig_friend_enemy = px.bar(
                friend_enemy_df,
                x='batch_name',
                y='count',
                color='relationship_status',
                title='বন্ধু-শত্রু তুলনামূলক চিত্র',
                color_discrete_map={
                    'Friend': '#2ecc71',  # Green
                    'Enemy': '#e74c3c'    # Red
                },
                barmode='group'
            )

            fig_friend_enemy.update_layout(
                xaxis_title="ব্যাচের নাম",
                yaxis_title="সংখ্যা",
                plot_bgcolor='white'
            )

            st.plotly_chart(fig_friend_enemy, use_container_width=True)

            # Calculate Friend-Enemy ratios and detailed metrics
            friend_counts = friend_enemy_df[friend_enemy_df['relationship_status'] == 'Friend'].groupby('batch_name')['count'].sum()
            enemy_counts = friend_enemy_df[friend_enemy_df['relationship_status'] == 'Enemy'].groupby('batch_name')['count'].sum()

            # Show metrics for each batch
            for batch in friend_counts.index:
                cols = st.columns(4)
                friend_count = friend_counts.get(batch, 0)
                enemy_count = enemy_counts.get(batch, 0)
                total = friend_count + enemy_count

                with cols[0]:
                    st.metric(f"ব্যাচ {batch}", f"মোট: {total}")
                with cols[1]:
                    st.metric("বন্ধু", friend_count)
                with cols[2]:
                    st.metric("শত্রু", enemy_count)
                with cols[3]:
                    ratio = friend_count / enemy_count if enemy_count > 0 else float('inf')
                    st.metric("অনুপাত", f"{ratio:.2f}" if ratio != float('inf') else "∞")

if __name__ == "__main__":
    relationship_stats_page()