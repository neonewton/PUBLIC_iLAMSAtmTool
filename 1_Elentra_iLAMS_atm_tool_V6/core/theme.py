import streamlit as st

import streamlit as st

def apply_ntu_purple_theme():
    st.markdown(
        """
        <style>
        /* ===== Base App ===== */
        .stApp {
            background-color: #EEF2F6;
            color: #1F2937;
        }

        /* ===== Top Header Bar ===== */
        header[data-testid="stHeader"] {
            background-color: #5A003E; /* NTU / LKC purple */
            height: 70px;
        }

        header[data-testid="stHeader"]::before {
            content: "NANYANG TECHNOLOGICAL UNIVERSITY  |  LEE KONG CHIAN SCHOOL OF MEDICINE";
            color: white;
            font-weight: 600;
            font-size: 16px;
            padding-left: 24px;
            line-height: 70px;
            display: block;
        }

        /* Hide default Streamlit header content */
        header[data-testid="stHeader"] > div {
            display: none;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E5E7EB;
        }

        /* ===============================
        NUMBER INPUT
        =============================== */

        div[data-testid="stNumberInput"] input {
            background-color: #FFFFFF !important;
            color: #111827 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 6px !important;
        }

        /* Spinner buttons (+ / -) */
        div[data-testid="stNumberInput"] button {
            background-color: #F9FAFB !important;
            border: 1px solid #CBD5E1 !important;
            color: #374151 !important;
        }

        /* ===============================
        FORM SUBMIT + BUTTONS
        =============================== */

        /* Primary */
        button[kind="primary"],
        div[data-testid="stForm"] input[type="submit"][kind="primary"] {
            background-color: #5A003E !important;
            color: #FFFFFF !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: 500 !important;
        }

        /* Primary hover */
        button[kind="primary"]:hover,
        div[data-testid="stForm"] input[type="submit"][kind="primary"]:hover {
            background-color: #7A0055 !important;
        }

        /* Secondary */
        button[kind="secondary"],
        div[data-testid="stForm"] input[type="submit"][kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #5A003E !important;
            border-radius: 6px !important;
            border: 1px solid #5A003E !important;
            font-weight: 500 !important;
        }

        /* Secondary hover */
        button[kind="secondary"]:hover,
        div[data-testid="stForm"] input[type="submit"][kind="secondary"]:hover {
            background-color: #F8EDF4 !important;
        }

        /* ===== Inputs (text input, select) ===== */
        input, select {
            border-radius: 6px !important;
            border: 1px solid #CBD5E1 !important;
            background-color: #FFFFFF !important;
            color: #111827 !important;
        }

        /* ===== Text Area ===== */
        textarea {
            border-radius: 6px !important;
            border: 1px solid #CBD5E1 !important;
            background-color: #FFFFFF !important;
            color: #111827 !important;
        }


        /* ===== Dataframes ===== */
        .stDataFrame {
            background-color: white;
            border-radius: 8px;
        }

        /* ===== Remove Streamlit Branding ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_claude_theme():
    st.markdown(
        """
        <style>
        /* ===== Base ===== */
        .stApp {
            background-color: #FAFAF7;
            color: #2E2E2E;
            font-family: "Inter", system-ui, sans-serif;
        }

        /* ===== Header ===== */
        header[data-testid="stHeader"] {
            background-color: #FAFAF7;
            border-bottom: 1px solid #E6E6E6;
        }

        /* ===== Sidebar ===== */
        section[data-testid="stSidebar"] {
            background-color: #F4F4F2;
            border-right: 1px solid #E6E6E6;
        }

        /* ===== Headings ===== */
        h1, h2, h3 {
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        /* ===== Buttons ===== */
        .stButton > button {
            background-color: #111827;
            color: #FAFAF7;
            border-radius: 10px;
            padding: 0.6em 1.4em;
            font-weight: 500;
            border: none;
        }

        .stButton > button:hover {
            background-color: #1F2937;
        }

        /* ===== Inputs ===== */
        input, textarea {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            border: 1px solid #D1D5DB !important;
            padding: 0.55em !important;
        }

        /* ===== Dataframes ===== */
        .stDataFrame {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
        }

        /* ===== Links ===== */
        a {
            color: #2563EB;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        /* ===== Remove Streamlit Branding ===== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
