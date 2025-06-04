import streamlit as st
import pandas as pd
import plotly.express as px
import io
from weasyprint import HTML

st.title("Portfolio Report MVP with PDF Export")

uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Portfolio Data")
    st.dataframe(df)

    df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce")
    df["Return (YTD)"] = df["Return (YTD)"].str.replace('%', '').astype(float)

    # Create charts
    pie_fig = px.pie(df, names="Asset Name", values="Market Value", title="Allocation by Market Value")
    bar_fig = px.bar(df, x="Asset Name", y="Return (YTD)", color="Asset Type", title="YTD Return by Asset")

    st.subheader("📈 Asset Allocation")
    st.plotly_chart(pie_fig)

    st.subheader("📊 Performance (YTD Return)")
    st.plotly_chart(bar_fig)

    # Generate summary text
    total_value = df["Market Value"].sum()
    weighted_return = (df["Market Value"] * df["Return (YTD)"]).sum() / total_value
    best_asset = df.loc[df["Return (YTD)"].idxmax()]
    worst_asset = df.loc[df["Return (YTD)"].idxmin()]

    summary = (
        f"Your portfolio's total market value is ${total_value:,.0f}.<br>"
        f"The weighted average return year-to-date is {weighted_return:.2f}%.<br>"
        f"The best performing asset is {best_asset['Asset Name']} with a return of {best_asset['Return (YTD)']:.2f}%.<br>"
        f"The worst performing asset is {worst_asset['Asset Name']} with a return of {worst_asset['Return (YTD)']:.2f}%."
    )

    st.subheader("📄 Portfolio Summary")
    st.markdown(summary, unsafe_allow_html=True)

    # Convert Plotly charts to PNG bytes
    pie_bytes = pie_fig.to_image(format="png")
    bar_bytes = bar_fig.to_image(format="png")

    # Create HTML content for PDF
    html_content = f"""
    <h1>Portfolio Report</h1>
    <h2>Summary</h2>
    <p>{summary}</p>
    <h2>Charts</h2>
    <img src="data:image/png;base64,{pie_bytes.hex()}" width="400" />
    <img src="data:image/png;base64,{bar_bytes.hex()}" width="400" />
    """

    # Convert to PDF bytes
    pdf = HTML(string=html_content).write_pdf()

    # Provide a download button
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf,
        file_name="portfolio_report.pdf",
        mime="application/pdf"
    )
else:
    st.write("Please upload a CSV file to see your data.")
