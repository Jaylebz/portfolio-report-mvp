import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from weasyprint import HTML

st.title("Portfolio Report MVP with PDF Export")

def fig_to_base64(fig):
    img_bytes = fig.to_image(format="png")
    base64_str = base64.b64encode(img_bytes).decode()
    return base64_str

uploaded_file = st.file_uploader("Upload your portfolio CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📋 Portfolio Data")
    st.dataframe(df)

    df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce")
    df["Return (YTD)"] = df["Return (YTD)"].str.replace('%', '').astype(float)

    pie_fig = px.pie(df, names="Asset Name", values="Market Value", title="Allocation by Market Value")
    bar_fig = px.bar(df, x="Asset Name", y="Return (YTD)", color="Asset Type", title="YTD Return by Asset")

    st.subheader("📈 Asset Allocation")
    st.plotly_chart(pie_fig)

    st.subheader("📊 Performance (YTD Return)")
    st.plotly_chart(bar_fig)

    total_value = df["Market Value"].sum()
    weighted_return = (df["Market Value"] * df["Return (YTD)"]).sum() / total_value
    best_asset = df.loc[df["Return (YTD)"].idxmax()]
    worst_asset = df.loc[df["Return (YTD)"].idxmin()]

    summary_html = (
        f"Your portfolio's total market value is ${total_value:,.0f}.<br>"
        f"The weighted average return year-to-date is {weighted_return:.2f}%.<br>"
        f"The best performing asset is {best_asset['Asset Name']} with a return of {best_asset['Return (YTD)']:.2f}%.<br>"
        f"The worst performing asset is {worst_asset['Asset Name']} with a return of {worst_asset['Return (YTD)']:.2f}%."
    )

    st.subheader("📄 Portfolio Summary")
    st.markdown(summary_html, unsafe_allow_html=True)

    pie_base64 = fig_to_base64(pie_fig)
    bar_base64 = fig_to_base64(bar_fig)

    html_report = f"""
    <html>
    <head><title>Portfolio Report</title></head>
    <body>
        <h1>Portfolio Report</h1>
        <h2>Summary</h2>
        <p>{summary_html}</p>
        <h2>Charts</h2>
        <img src="data:image/png;base64,{pie_base64}" width="400" />
        <img src="data:image/png;base64,{bar_base64}" width="400" />
    </body>
    </html>
    """

    pdf_bytes = HTML(string=html_report).write_pdf()

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name="portfolio_report.pdf",
        mime="application/pdf"
    )
else:
    st.write("Please upload a CSV file to see your data.")
