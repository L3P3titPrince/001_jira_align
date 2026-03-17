import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def create_sankey_diagram():
    """
    Reads the three CSV reports and generates a professional, interactive
    Sankey diagram showing the relationship flow.
    """
    print("--- Starting Sankey Diagram Generation ---")

    data_path = Path(__file__).resolve().parent.parent / 'data'
    output_path = Path(__file__).resolve().parent.parent / 'output'
    output_path.mkdir(exist_ok=True)

    # --- Step 1: Load the data ---
    try:
        initiatives_df = pd.read_csv(data_path / 'initiatives_report.csv')
        features_df = pd.read_csv(data_path / 'epic_features_report.csv')
        dependencies_df = pd.read_csv(data_path / 'dependencies_report.csv')
        print("Successfully loaded all three report files.")
    except Exception as e:
        return print(f"Error loading files: {e}")

    # --- Step 2: Prepare the data for the Sankey diagram ---
    # We need to create a single list of all unique nodes (Initiatives, Features, etc.)
    # and then create a mapping from their ID to a numerical index (0, 1, 2, ...).
    
    # Create unique labels for each node
    initiatives_df['label'] = initiatives_df['initiative_title'].fillna('No Title')
    features_df['label'] = features_df['epic_title'].fillna('No Title')
    dependencies_df['label'] = dependencies_df['dependency_title'].fillna('No Title')
    
    # Create unique node IDs
    initiatives_df['node_id'] = 'I' + initiatives_df['initiative_id'].astype(str)
    features_df['node_id'] = 'F' + features_df['epic_id'].astype(str)
    dependencies_df['node_id'] = 'D' + dependencies_df['dependency_id'].astype(str)

    # Combine all unique nodes into one list
    all_nodes = pd.concat([
        initiatives_df[['node_id', 'label']],
        features_df[['node_id', 'label']],
        dependencies_df[['node_id', 'label']]
    ]).drop_duplicates(subset=['node_id']).reset_index(drop=True)
    
    # Create the mapping from node ID string to its index
    node_map = {node_id: i for i, node_id in enumerate(all_nodes['node_id'])}

    # --- Step 3: Create the links (source -> target) ---
    links = []

    # Links from Features to Initiatives
    for _, row in features_df.iterrows():
        if pd.notna(row['initiative_id']) and pd.notna(row['epic_id']):
            source_id = f"F{row['epic_id']}"
            target_id = f"I{row['initiative_id']}"
            if source_id in node_map and target_id in node_map:
                links.append({
                    'source': node_map[source_id],
                    'target': node_map[target_id]
                })

    # Links from Dependencies to Features
    for _, row in dependencies_df.iterrows():
        if pd.notna(row['epic_id']) and pd.notna(row['dependency_id']):
            source_id = f"D{row['dependency_id']}"
            target_id = f"F{row['epic_id']}"
            if source_id in node_map and target_id in node_map:
                links.append({
                    'source': node_map[source_id],
                    'target': node_map[target_id]
                })

    print(f"\n--- Graph Construction Complete ---")
    print(f"Total Unique Nodes: {len(all_nodes)}")
    print(f"Total Links created: {len(links)}")

    if not links:
        return print("No links could be created. Cannot generate Sankey diagram.")

    # --- Step 4: Create the Sankey Diagram Figure ---
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = all_nodes['label'].tolist(),
          color = "blue"
        ),
        link = dict(
          source = [link['source'] for link in links],
          target = [link['target'] for link in links],
          value = [1] * len(links) # Give each link a base value of 1
      ))])

    fig.update_layout(title_text="Initiative -> Feature -> Dependency Flow", font_size=12)

    # --- Step 5: Save the figure as a standalone HTML file ---
    try:
        output_filename = output_path / 'sankey_flow_diagram.html'
        fig.write_html(str(output_filename))
        print(f"\n--- SUCCESS! ---")
        print(f"Sankey diagram saved to: {output_filename}")
        print("You can now open this HTML file in your web browser.")
    except Exception as e:
        print(f"An error occurred during HTML generation: {e}")

if __name__ == '__main__':
    create_sankey_diagram()
