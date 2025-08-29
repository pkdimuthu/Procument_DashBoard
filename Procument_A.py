import streamlit as st
import pandas as pd
import os
import plotly.express as px

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("Procurement Dashboard")
page = st.sidebar.radio("Select Page", ["Purchasing", "Construction", "Medical Equipment"])

# -----------------------------
# Helper function to display table with persistent CSV storage
# -----------------------------
def display_procurement_page(page_name):
    st.title(f"{page_name} Procurement Dashboard")
    st.write("Upload your CSV file with procurement details:")

    save_path = f"{page_name.lower()}_procurement_saved.csv"

    uploaded_file = st.file_uploader(f"Upload {page_name} CSV", type=["csv"])

    # Load Data
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df.to_csv(save_path, index=False)  # Save persistently
    else:
        if os.path.exists(save_path):
            df = pd.read_csv(save_path)
        else:
            st.info("Please upload a CSV file to begin.")
            return

    # Ensure required columns exist
    required_cols = [
        "Item", "Start_Date", "End_Date",
        "Paper_Add_Date", "Tender_Open_Date", "Doc_sent_TC_Date",
        "TC_Deci_Received_Date", "Proc_Com_Hand_Date", "Po_Issued_Date",
        "Status"
    ]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return

    # Add missing 'Comment' column if not in CSV
    if "Comment" not in df.columns:
        df["Comment"] = ""

    # Convert date columns
    for col in ["Start_Date", "End_Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # -----------------------------
    # Status update section
    # -----------------------------
    st.subheader("Update Procurement Status")
    selected_item = st.selectbox("Select Item", df["Item"])
    new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed", "Delayed"])
    comment = st.text_input("Officer Comment", "")

    if st.button("Update Status"):
        df.loc[df["Item"] == selected_item, ["Status", "Comment"]] = [new_status, comment]
        df.to_csv(save_path, index=False)
        st.success(f"Status updated for {selected_item} → {new_status}")

    # -----------------------------
    # Data Display
    # -----------------------------
    st.subheader("Procurement Records")
    st.dataframe(df)

    # -----------------------------
    # Charts
    # -----------------------------
    st.subheader("Visual Analytics")

    # 1. Timeline chart
    fig = px.timeline(
        df,
        x_start="Start_Date",
        x_end="End_Date",
        y="Item",
        color="Status",
        text="Comment",
        title="Procurement Timeline"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    # 2. Status distribution bar chart
    status_counts = df["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig2 = px.bar(
        status_counts,
        x="Status",
        y="Count",
        color="Status",
        title="Procurement Status Distribution",
        text="Count"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # -----------------------------
    # Download CSV
    # -----------------------------
    st.download_button(
        label="Download Updated CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"{page_name.lower()}_procurement_updated.csv",
        mime="text/csv"
    )


# -----------------------------
# Render selected page
# -----------------------------
if page == "Purchasing":
    display_procurement_page("Purchasing")
elif page == "Construction":
    display_procurement_page("Construction")
else:
    display_procurement_page("Medical Equipment")

