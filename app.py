import streamlit as st
import pandas as pd
import plotly.express as px
import smtplib
from email.mime.text import MIMEText
from PIL import Image
import io

# --- Header and Logo Upload (optional) ---
st.markdown('<h1 class="main-title">📊 Portfolio Report Generator</h1>', unsafe_allow_html=True)

logo_file = st.file_uploader("Upload your Firm Logo (optional, PNG/JPG)", type=["png", "jpg", "jpeg"])
if logo_file is not None:
    image = Image.open(logo_file)
    st.image(image, width=180)

# --- Firm and client info ---
firm_name = st.text_input("Firm Name", value="Your Firm")
client_name = st.text_input("Client Name", value="Client A")

# Editable footer contact info
footer_contact = st.text_input("Footer Contact Email", value="contact@yourfirm.com")
footer_website = st.text_input("Footer Website URL", value="https://yourfirm.com")

# --- Input method ---
input_method = st.radio("How do you want to enter portfolio data?", ["Upload CSV/Excel", "Manual Entry"])

if "assets" not in st.session_state:
    st.session_state.assets = []

df = None

# --- Sample CSV content and instructions ---
st.markdown("""
**Please upload a CSV or Excel file with these columns exactly:**  
- Asset Name  
- Asset Type  
- Market Value  
- Return (YTD)  

You can download a sample file here and use it as a template.
""")

sample_csv = """Asset Name,Asset Type,Market Value,Return (YTD)
Apple Inc,Stock,100000,12.5
Vanguard Total Bond Market,Bond,50000,3.2
Cash,Cash,20000,0
"""

st.download_button(
    label="Download Sample CSV Template",
    data=sample_csv,
    file_name="sample_portfolio_template.csv",
    mime="text/csv"
)

import io

sample_data = {
    "Asset Name": ["Apple Inc", "Vanguard Total Bond Market", "Cash"],
    "Asset Type": ["Stock", "Bond", "Cash"],
    "Market Value": [100000, 50000, 20000],
    "Return (YTD)": [12.5, 3.2, 0]
}
sample_df = pd.DataFrame(sample_data)

output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    sample_df.to_excel(writer, index=False, sheet_name='Portfolio')

output.seek(0)

st.download_button(
    label="Download Sample Excel Template",
    data=output,
    file_name="sample_portfolio_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- CSV or Excel Upload ---
if input_method == "Upload CSV/Excel":
    uploaded_file = st.file_uploader("Upload your portfolio CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)

            # Validate required columns
            required_cols = {"Asset Name", "Asset Type", "Market Value", "Return (YTD)"}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                st.error(f"Uploaded file is missing required columns: {', '.join(missing)}. Please fix and re-upload.")
                df = None
            else:
                # Process columns
                df["Market Value"] = pd.to_numeric(df["Market Value"], errors="coerce")
                if df["Return (YTD)"].dtype == object:
                    df["Return (YTD)"] = df["Return (YTD)"].str.replace('%', '').astype(float)

        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            df = None

# --- Manual Entry ---
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

# --- Portfolio report and visualizations ---
if df is not None and not df.empty:
    st.subheader("📋 Portfolio Data")
    st.dataframe(df)

    st.subheader("📈 Asset Allocation")
    pie_fig = px.pie(
        df,
        names="Asset Name",
        values="Market Value",
        title="Allocation by Market Value",
        color_discrete_sequence=["#0D3B66", "#145374", "#1E6F9F", "#2A99D8", "#58C9F3"]
    )
    st.plotly_chart(pie_fig)

    st.subheader("📊 Performance (YTD Return)")
    bar_fig = px.bar(
        df,
        x="Asset Name",
        y="Return (YTD)",
        color="Asset Type",
        title="YTD Return by Asset",
        color_discrete_sequence=["#0D3B66", "#145374", "#1E6F9F", "#2A99D8", "#58C9F3"]
    )
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

    # --- Build downloadable report with branding ---
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
    report_text += (
        f"\n{'-'*30}\n"
        f"Report generated by {firm_name} Portfolio Report Generator\n"
        f"Contact: {footer_contact} | {footer_website}\n"
    )

    st.subheader("📄 Downloadable Report")
    st.download_button(
        label="📥 Download Report",
        data=report_text,
        file_name=f"{client_name.lower().replace(' ', '_')}_portfolio_report.txt",
        mime="text/plain"
    )

    # --- Email sending section ---
    st.subheader("📧 Send Report by Email")

    recipient_email = st.text_input("Recipient Email")
    sender_email = st.text_input("Your Gmail Address")
    sender_password = st.text_input("Your Gmail App Password", type="password")
    send_button = st.button("Send Report")

    def send_email_report(to_email, subject, body, from_email, from_password):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())

    if send_button:
        if recipient_email and sender_email and sender_password:
            try:
                send_email_report(
                    to_email=recipient_email,
                    subject=f"{firm_name} - Portfolio Report for {client_name}",
                    body=report_text,
                    from_email=sender_email,
                    from_password=sender_password
                )
                st.success("Email sent successfully!")
            except Exception as e:
                st.error(f"Error sending email: {e}")
        else:
            st.error("Please fill in all email fields.")

else:
    st.info("Please upload a CSV/Excel file or add at least one asset manually.")

# --- Footer ---
st.markdown(
    f"""
    <div class="footer">
    © 2025 {firm_name} - All rights reserved | Contact: {footer_contact} | <a href="{footer_website}" target="_blank">{footer_website}</a>
    </div>
    """,
    unsafe_allow_html=True
)
