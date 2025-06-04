import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Portfolio Report Generator (MVP)")

# Firm and client info
firm_name = st.text_input("Firm Name", value="Your Firm")
client_name = st.text_input("Client Name", value="Client A")

# File upload
uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Portfolio Data")
    st.dataframe(df)

    # Convert values
    df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce")
    df["Return (YTD)"] = df["Return (YTD)"].str.replace('%', '').astype(float)

    st.subheader("📈 Asset Allocation")
    pie_fig = px.pie(df, names="Asset Name", values="Market Value", title="Allocation by Market Value")
    st.plotly_chart(pie_fig)

    st.subheader("📊 Performance (YTD Return)")
    bar_fig = px.bar(df, x="Asset Name", y="Return (YTD)", color="Asset Type", title="YTD Return by Asset")
    st.plotly_chart(bar_fig)

    # Rule-based summary
    total_value = df["Market Value"].sum()
    weighted_return = (df["Market Value"] * df["Return (YTD)"]).sum() / total_value
    best_asset = df.loc[df["Return (YTD)"].idxmax()]
    worst_asset = df.loc[df["Return (YTD)"].idxmin()]

    summary = (
        f"Your portfolio's total market value is ${total_value:,.0f}.\n"
        f"The weighted average return year-to-date is {weighted_return:.2f}%.\n"
        f"The best performing asset is {best_asset['Asset Name']} "
        f"with a return of {best_asset['Return (YTD)']:.2f}%.\n"
        f"The worst performing asset is {worst_asset['Asset Name']} "
        f"with a return of {worst_asset['Return (YTD)']:.2f}%."
    )

    st.subheader("📄 Portfolio Summary")
    st.text(summary)

    # Downloadable report
    st.subheader("📄 Downloadable Report")

    report_text = (
        f"{firm_name} - Client Report\n"
        f"Client: {client_name}\n"
        f"{'-'*30}\n\n"
        f"Portfolio Summary\n------------------\n{summary}\n\nAssets:\n"
    )

    for i, row in df.iterrows():
        report_text += (
            f"- {row['Asset Name']}: "
            f"Type: {row['Asset Type']}, "
            f"Market Value: ${row['Market Value']:,.0f}, "
            f"YTD Return: {row['Return (YTD)']:.2f}%\n"
        )

    st.download_button(
        label="📥 Download Report",
        data=report_text,
        file_name=f"{client_name.lower().replace(' ', '_')}_portfolio_report.txt",
        mime="text/plain"
    )

else:
    st.info("Please upload a CSV file to see your report.")
