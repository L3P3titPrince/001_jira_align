import plotly.graph_objects as go
import pandas as pd
import os

# Get the directory of the current script (/src)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')

# Construct the path to the CSV file
csv_path = os.path.join(project_root, 'data', '004_idea_flow.csv')

# 1. Read the data from the CSV file
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: '{csv_path}' not found. Please ensure the file exists.")
    exit()

# 2. Define the nodes and calculate their totals
all_labels_from_data = pd.concat([df['source'], df['target']]).unique()
labels = list(all_labels_from_data)
node_totals = {}
for label in labels:
    total_out = df[df['source'] == label]['value'].sum()
    total_in = df[df['target'] == label]['value'].sum()
    node_totals[label] = max(total_in, total_out)

formatted_labels = [f"{label}\n{int(node_totals.get(label, 0))}" for label in labels]

# 3. Prepare data for Plotly
label_to_index = {label: i for i, label in enumerate(labels)}
source = df['source'].map(label_to_index)
target = df['target'].map(label_to_index)
value = df['value']

# Define colors for the links based on the 'type' column
color_map = {
    'flow': 'rgba(40, 167, 69, 0.6)',      # Green
    'dropped': 'rgba(220, 53, 69, 0.6)',   # Red
    'backlog': 'rgba(65, 105, 225, 0.6)'   # Royal Blue
}
link_colors = df['type'].map(color_map)

# 4. Create the Sankey figure
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
        color=link_colors
    )
)])

fig.update_layout(
    title_text="Idea Funnel Visualization",
    font_size=12
)

# --- Start of New Code ---

# 5. Save the figure to an HTML file
# Create an 'output' directory if it doesn't exist
output_dir = os.path.join(project_root, 'output')
os.makedirs(output_dir, exist_ok=True)

# Define the full path for the HTML file
html_path = os.path.join(output_dir, '004_idea_funnel_report.html')

# Write the figure to the HTML file
fig.write_html(html_path)

print(f"\nSUCCESS: Report saved to '{html_path}'")

# --- End of New Code ---

# 6. Show the dynamic figure in a browser window
fig.show()
