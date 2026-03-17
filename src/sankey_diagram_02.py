import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def create_sankey_diagram():
    """
    Reads the three CSV reports and generates a professional, interactive
    Sankey diagram with detailed labels and interactive hover text.
    """
    print("--- Starting Enhanced Sankey Diagram Generation ---")

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

    # =========================================================================
    # === NEW FEATURE 1: Create Enhanced Labels and Hover Text ===
    # =========================================================================
    
    # Create unique, descriptive labels for each node
    initiatives_df['label'] = initiatives_df['initiative_title'].fillna('No Title')
    features_df['label'] = features_df['epic_title'].fillna('No Title')
    dependencies_df['label'] = dependencies_df['dependency_title'].fillna('No Title')
    
    # Create the detailed hover text for each node
    initiatives_df['hover_text'] = initiatives_df.apply(lambda row: f"Initiative ID: {int(row['initiative_id'])}<br>{row['label']}", axis=1)
    features_df['hover_text'] = features_df.apply(lambda row: f"Epic ID: {int(row['epic_id'])}<br>{row['label']}", axis=1)
    dependencies_df['hover_text'] = dependencies_df.apply(lambda row: f"Dependency ID: {int(row['dependency_id'])}<br>{row['label']}", axis=1)
    
    # Create unique node IDs
    initiatives_df['node_id'] = 'I' + initiatives_df['initiative_id'].astype(str)
    features_df['node_id'] = 'F' + features_df['epic_id'].astype(str)
    dependencies_df['node_id'] = 'D' + dependencies_df['dependency_id'].astype(str)

    # Combine all unique nodes into one list, now including the hover_text
    all_nodes = pd.concat([
        initiatives_df[['node_id', 'label', 'hover_text']],
        features_df[['node_id', 'label', 'hover_text']],
        dependencies_df[['node_id', 'label', 'hover_text']]
    ]).drop_duplicates(subset=['node_id']).reset_index(drop=True)
    
    # Create the mapping from node ID string to its index
    node_map = {node_id: i for i, node_id in enumerate(all_nodes['node_id'])}

    # --- Step 3: Create the links (source -> target) ---
    links = []
    valid_feature_ids = set(features_df['epic_id'].dropna().astype(int))

    for _, row in features_df.iterrows():
        if pd.notna(row['initiative_id']) and pd.notna(row['epic_id']):
            links.append({'source': node_map[f"F{int(row['epic_id'])}"], 'target': node_map[f"I{int(row['initiative_id'])}"]})

    for _, row in dependencies_df.iterrows():
        if pd.notna(row['epic_id']) and int(row['epic_id']) in valid_feature_ids:
            if pd.notna(row['dependency_id']):
                links.append({'source': node_map[f"D{int(row['dependency_id'])}"], 'target': node_map[f"F{int(row['epic_id'])}"]})

    print(f"\n--- Graph Construction Complete ---")
    print(f"Total Unique Nodes: {len(all_nodes)}, Total VALID Links created: {len(links)}")

    if not links: return print("No valid links found. Cannot generate diagram.")

    # =========================================================================
    # === NEW FEATURE 2: Add Hover Information to the Sankey Diagram ===
    # =========================================================================
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = all_nodes['label'].tolist(),
          # Pass the hover text as custom data
          customdata = all_nodes['hover_text'].tolist(),
          # Define the hover template to show the custom data
          hovertemplate='<b>%{customdata}</b><extra></extra>',
          color = "blue"
        ),
        link = dict(
          source = [link['source'] for link in links],
          target = [link['target'] for link in links],
          value = [1] * len(links)
      ))])

    fig.update_layout(title_text="Initiative -> Feature -> Dependency Flow", font_size=12)

    # --- Step 5: Save the figure ---
    try:
        output_filename = output_path / 'sankey_diagram_with_details.html'
        fig.write_html(str(output_filename))
        print(f"\n--- SUCCESS! ---")
        print(f"Sankey diagram saved to: {output_filename}")
    except Exception as e:
        print(f"An error occurred during HTML generation: {e}")

if __name__ == '__main__':
    create_sankey_diagram()
