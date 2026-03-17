import plotly.graph_objects as go

# 1. Define the nodes (stages) of the income statement
# The order determines the index we use to connect flows.
labels = [
    # Revenue Side (Indices 0-7)
    "Search advertising", "YouTube", "Google network", "Playstore & other",
    "Google Cloud", "Other revenue", "Ad revenue", "Revenue",
    # Cost & Expense Side (Indices 8-14)
    "Cost of revenue", "Traffic acquisition costs", "Content acquisition, data centers, other",
    "Operating expenses", "R&D", "Sales & marketing", "General & admin",
    # Profit Side (Indices 15-20)
    "Gross profit", "Operating profit", "Other income", "Income Before Tax",
    "Net profit", "Tax"
]

# 2. Define the flows between nodes (source, target, value) and their colors
flows = [
    # Ad Revenue components -> Ad revenue
    {"source": 0, "target": 6, "value": 54.2, "color": "rgba(200, 200, 200, 0.6)"},
    {"source": 1, "target": 6, "value": 9.8, "color": "rgba(200, 200, 200, 0.6)"},
    {"source": 2, "target": 6, "value": 7.4, "color": "rgba(200, 200, 200, 0.6)"},
    # All revenue streams -> Total Revenue
    {"source": 6, "target": 7, "value": 71.3, "color": "rgba(200, 200, 200, 0.6)"},
    {"source": 3, "target": 7, "value": 11.2, "color": "rgba(200, 200, 200, 0.6)"},
    {"source": 4, "target": 7, "value": 13.6, "color": "rgba(200, 200, 200, 0.6)"},
    {"source": 5, "target": 7, "value": 0.3, "color": "rgba(200, 200, 200, 0.6)"},
    # Revenue -> Gross Profit (green) and Cost of Revenue (red)
    {"source": 7, "target": 15, "value": 57.4, "color": "rgba(40, 167, 69, 0.6)"},
    {"source": 7, "target": 8, "value": 39.0, "color": "rgba(220, 53, 69, 0.6)"},
    # Cost of Revenue breakdown
    {"source": 8, "target": 9, "value": 14.7, "color": "rgba(220, 53, 69, 0.6)"},
    {"source": 8, "target": 10, "value": 24.3, "color": "rgba(220, 53, 69, 0.6)"},
    # Gross Profit -> Operating Profit (green) and Operating Expenses (red)
    {"source": 15, "target": 16, "value": 31.3, "color": "rgba(40, 167, 69, 0.6)"},
    {"source": 15, "target": 11, "value": 26.1, "color": "rgba(220, 53, 69, 0.6)"},
    # Operating Expenses breakdown
    {"source": 11, "target": 12, "value": 13.8, "color": "rgba(220, 53, 69, 0.6)"},
    {"source": 11, "target": 13, "value": 7.1, "color": "rgba(220, 53, 69, 0.6)"},
    {"source": 11, "target": 14, "value": 5.2, "color": "rgba(220, 53, 69, 0.6)"},
    # Profit Before Tax -> Net Profit (green) and Tax (red)
    {"source": 16, "target": 18, "value": 31.3, "color": "rgba(40, 167, 69, 0.6)"},
    {"source": 17, "target": 18, "value": 2.7, "color": "rgba(40, 167, 69, 0.6)"},
    {"source": 18, "target": 19, "value": 28.2, "color": "rgba(40, 167, 69, 0.6)"},
    {"source": 18, "target": 20, "value": 5.7, "color": "rgba(220, 53, 69, 0.6)"}
]

# 3. Prepare the data for the Plotly figure object
source = [flow["source"] for flow in flows]
target = [flow["target"] for flow in flows]
value = [flow["value"] for flow in flows]
link_colors = [flow["color"] for flow in flows]

# 4. Add values to node labels to mimic the original chart
label_values = {
    "Search advertising": 54.2, "YouTube": 9.8, "Google network": 7.4,
    "Playstore & other": 11.2, "Google Cloud": 13.6, "Other revenue": 0.3,
    "Ad revenue": 71.3, "Revenue": 96.4, "Cost of revenue": 39.0,
    "Traffic acquisition costs": 14.7, "Content acquisition, data centers, other": 24.3,
    "Operating expenses": 26.1, "R&D": 13.8, "Sales & marketing": 7.1,
    "General & admin": 5.2, "Gross profit": 57.4, "Operating profit": 31.3,
    "Other income": 2.7, "Income Before Tax": 34.0, "Net profit": 28.2, "Tax": 5.7
}
formatted_labels = [f"{label}<br>${label_values.get(label, 0)}B" for label in labels]
# We hide the intermediate "Income Before Tax" node to clean up the final stage
formatted_labels[18] = "" # Index of "Income Before Tax"

# 5. Create and display the Sankey figure
fig = go.Figure(data=[go.Sankey(
    node=dict(
      pad=25,
      thickness=20,
      line=dict(color="black", width=0.5),
      label=formatted_labels,
      color="gainsboro"
    ),
    link=dict(
      source=source,
      target=target,
      value=value,
      color=link_colors # Apply custom colors to the flows
  ))])

fig.update_layout(
    title_text="Alphabet Q2 FY25 Income Statement (Recreated)",
    font_size=12
)

fig.show()

