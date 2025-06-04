import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import BytesIO
from weasyprint import HTML

def fig_to_base64(fig):
    img_bytes = fig.to_image(format="png")
    return base64.b64encode(img_bytes).decode()

def generate_html_report(summary_html, pie_b64, bar_b64):
    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
        p {{ font-size: 14px; line-height: 1.6; color: #444; }}
        .chart {{ margin-top: 20px; margin-bottom: 40px; text-align: center; }}
        img {{ max-width: 600px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    </style>
    </head>
    <body>
        <h1>Portfolio Report</h1>
        <h2>Summary</h2>
        <p>{summary_html}</p>
        <h2>Asset Allocation</h2>
        <div class="chart">
            <img src="data:image/png;base64,{pie_b64}" alt="Pie Chart">
        </div>
        <h2>Performance (YTD Return)</h2>
        <div class="chart">
            <img src="data:image/png;base64,{bar_b64}" alt="Bar Chart">
        </div>
    </body>
    </html>
    """
    return html

st.title("Portfolio Report MVP with Styled PDF Export")

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

    # Convert charts to base64 images
    pie_b64 = fig_to_base64(pie_fig)
    bar_b64 = fig_to_base64(bar_fig)

    # Generate HTML report
    html_report = generate_html_report(summary, pie_b64, bar_b64)

    # Convert HTML to PDF bytes
    pdf = HTML(string=html_report).write_pdf()

    # Download button
    st.download_button(
        label="📥 Download Styled PDF Report",
        data=pdf,
        file_name="portfolio_report.pdf",
        mime="application/pdf"
    )
else:
    st.write("Please upload a CSV file to see your data.")
