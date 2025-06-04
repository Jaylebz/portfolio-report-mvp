import streamlit as st
import pandas as pd

st.title("Portfolio Report MVP")

uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Here's your portfolio data:")
    st.dataframe(df)
else:
    st.write("Please upload a CSV file to see your data.")
