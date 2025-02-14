import streamlit as st

def apply_custom_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Tiro+Bangla:ital@0;1&display=swap');
        
        /* Global font settings */
        :lang(bn), .stMarkdown, .stText, h1, h2, h3, p, span, button, .stButton button, .stTextInput input, .stSelectbox select {
            font-family: 'Tiro Bangla', sans-serif !important;
        }
        
        /* Ensure Bengali text uses Tiro Bangla */
        *:not(code):not(pre) {
            font-family: 'Tiro Bangla', sans-serif;
        }
        
        /* Header styling */
        .stTitle {
            font-weight: bold;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f2f6;
        }
        
        /* Card styling */
        .stBlock {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Button styling */
.stButton button {
    width: 100%;
    border-radius: 0.9rem;
    font-weight: 500;
    background-color: black;
    color: white;
    border: none;
    transition: all 0.3s ease;
}

.stButton button:hover {
    background-color: white;
    color: black;
    border: 1px solid black;
}

        
        /* Search box styling */
        .stTextInput input {
            border-radius: 0.3rem;
        }
        
        /* Table styling */
        .stDataFrame {
            border: 1px solid #f0f2f6;
            border-radius: 0.5rem;
        }
        
        /* Alert/message styling */
        .stAlert {
            padding: 1rem;
            border-radius: 0.3rem;
        }
        </style>
    """, unsafe_allow_html=True)
