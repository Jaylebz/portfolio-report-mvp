import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Portfolio Report MVP")

uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Portfolio Data")
    st.dataframe(df)

    # Make sure Market Value is numeric
    df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce")
    df["Return (YTD)"] = df["Return (YTD)"].str.replace('%','').astype(float)

    st.subheader("📈 Asset Allocation")
    pie_fig = px.pie(df, names="Asset Name", values="Market Value", title="Allocation by Market Value")
    st.plotly_chart(pie_fig)

    st.subheader("📊 Performance (YTD Return)")
    bar_fig = px.bar(df, x="Asset Name", y="Return (YTD)", color="Asset Type", title="YTD Return by Asset")
    st.plotly_chart(bar_fig)
else:
    st.write("Please upload a CSV file to see your data.")
