import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# -------------------------------
# Load Data
# -------------------------------
df = pd.read_csv("architecture_pipeline_data.csv")
df["date"] = pd.to_datetime(df["date"])

# -------------------------------
# Filters
# -------------------------------
st.sidebar.header("Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    [df["date"].min(), df["date"].max()]
)

selected_sources = st.sidebar.multiselect(
    "Traffic Source",
    df["source"].unique(),
    default=df["source"].unique()
)

selected_services = st.sidebar.multiselect(
    "Service",
    df["service"].unique(),
    default=df["service"].unique()
)

filtered = df[
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1])) &
    (df["source"].isin(selected_sources)) &
    (df["service"].isin(selected_services))
]

# -------------------------------
# KPI Calculations
# -------------------------------
visitors = filtered[filtered["event"] == "visit"]["prospect_id"].nunique()
views = filtered[filtered["event"] == "view_project"]["prospect_id"].nunique()
enquiries = filtered[filtered["event"] == "enquiry"]["prospect_id"].nunique()
deals = filtered[filtered["event"] == "deal_closed"]["prospect_id"].nunique()
move_ins = filtered[filtered["event"] == "move_in"]["prospect_id"].nunique()

# Conversion rates
enquiry_rate = (enquiries / visitors * 100) if visitors else 0
deal_rate = (deals / enquiries * 100) if enquiries else 0
move_rate = (move_ins / deals * 100) if deals else 0

# -------------------------------
# Header
# -------------------------------
st.title("🏗️ Architecture Service Performance Dashboard")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Visitors", visitors)
c2.metric("Project Views", views)
c3.metric("Enquiries", f"{enquiries} ({enquiry_rate:.1f}%)")
c4.metric("Deals Closed", f"{deals} ({deal_rate:.1f}%)")
c5.metric("Move-ins", f"{move_ins} ({move_rate:.1f}%)")

st.markdown("---")

# -------------------------------
# Funnel
# -------------------------------
st.subheader("Client Journey Funnel")

funnel_df = pd.DataFrame({
    "Stage": ["Visit", "View", "Enquiry", "Deal", "Move-in"],
    "Count": [visitors, views, enquiries, deals, move_ins]
})

funnel_df["Rate (%)"] = funnel_df["Count"] / funnel_df["Count"].iloc[0] * 100

fig = px.funnel(funnel_df, x="Count", y="Stage", text=funnel_df["Rate (%)"].round(1))
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Drop-off
# -------------------------------
st.subheader("Client Journey Drop-off")

drop = []
stages = funnel_df["Stage"].tolist()
counts = funnel_df["Count"].tolist()

for i in range(len(stages)-1):
    loss = counts[i] - counts[i+1]
    pct = (loss / counts[i] * 100) if counts[i] else 0
    drop.append([f"{stages[i]} → {stages[i+1]}", loss, round(pct,1)])

drop_df = pd.DataFrame(drop, columns=["Stage Transition", "Lost", "Drop %"])
st.dataframe(drop_df)

# -------------------------------
# Service Performance
# -------------------------------
st.subheader("Service Performance")

service_perf = filtered.groupby("service").agg(
    enquiries=("event", lambda x: (x == "enquiry").sum()),
    deals=("event", lambda x: (x == "deal_closed").sum()),
    move_ins=("event", lambda x: (x == "move_in").sum())
).reset_index()

fig = px.bar(service_perf, x="service", y="move_ins", color="service")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Source Performance
# -------------------------------
st.subheader("Traffic Source Performance")

source_perf = filtered.groupby("source").agg(
    enquiries=("event", lambda x: (x == "enquiry").sum()),
    deals=("event", lambda x: (x == "deal_closed").sum()),
    move_ins=("event", lambda x: (x == "move_in").sum())
).reset_index()

fig = px.bar(source_perf, x="source", y="move_ins", color="source")
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Trend
# -------------------------------
st.subheader("Move-in Trend")

trend = filtered[filtered["event"] == "move_in"].groupby("date").size().reset_index(name="move_ins")

fig = px.line(trend, x="date", y="move_ins", markers=True)
st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Insights
# -------------------------------
st.subheader("Key Insights")

top_service = service_perf.sort_values("move_ins", ascending=False).iloc[0]
top_source = source_perf.sort_values("move_ins", ascending=False).iloc[0]
big_drop = drop_df.sort_values("Drop %", ascending=False).iloc[0]

st.write(
    f"🔥 **Top Service:** {top_service['service']} drives the highest completed projects."
)
st.write(
    f"📈 **Best Source:** {top_source['source']} generates the most successful move-ins."
)
st.write(
    f"⚠️ **Biggest Drop:** {big_drop['Stage Transition']} ({big_drop['Drop %']}%) needs optimization."
)

st.markdown("---")

# -------------------------------
# Raw Data
# -------------------------------
st.subheader("Raw Data")
st.dataframe(filtered)