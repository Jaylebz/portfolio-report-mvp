import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Portfolio Report Generator")

# Firm and client info
firm_name = st.text_input("Firm Name", value="Your Firm")
client_name = st.text_input("Client Name", value="Client A")

# Choose input method
input_method = st.radio("How do you want to enter portfolio data?", ["Upload CSV/Excel", "Manual Entry"])

# Initialize session asset list for manual entry
if "assets" not in st.session_state:
    st.session_state.assets = []

df = None  # Will hold the final DataFrame

# CSV or Excel Upload
if input_method == "Upload CSV/Excel":
    uploaded_file = st.file_uploader("Upload your portfolio CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        # Clean & convert columns
        df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce")

        if df["Return (YTD)"].dtype == object:
            df["Return (YTD)"] = df["Return (YTD)"].str.replace('%', '').astype(float)

# Manual Entry
else:
    with st.form("asset_form"):
        asset_name = st.text_input("Asset Name")
        asset_type = st.selectbox("Asset Type", ["Stock", "Bond", "ETF", "Mutual Fund", "Cash", "Other"])
        market_value = st.number_input("Market Value ($)", min_value=0.0, step=100.0, format="%.2f")
        ytd_return = st.number_input("YTD Return (%)", step=0.1, format="%.2f")
        submitted = st.form_submit_button("Add Asset")

        if submitted:
            st.session_state.assets.append({
                "Asset Name": asset_name,
                "Asset Type": asset_type,
                "Market Value": market_value,
                "Return (YTD)": ytd_return
            })

    if st.session_state.assets:
        df = pd.DataFrame(st.session_state.assets)

# If data is ready, generate report
if df is not None and not df.empty:
    st.subheader("📋 Portfolio Data")
    st.dataframe(df)

    st.subheader("📈 Asset Allocation")
    pie_fig = px.pie(df, names="Asset Name", values="Market Value", title="Allocation by Market Value")
    st.plotly_chart(pie_fig)

    st.subheader("📊 Performance (YTD Return)")
    bar_fig = px.bar(df, x="Asset Name", y="Return (YTD)", color="Asset Type", title="YTD Return by Asset")
    st.plotly_chart(bar_fig)

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
    st.info("Please upload a CSV/Excel file or add at least one asset manually.")
