import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

def create_prioritization_sankey():
    """
    Generates a Sankey diagram showing dependency-driven initiatives and all
    of their associated features to provide prioritization context.
    """
    print("--- Starting Prioritization Context Sankey Generation ---")

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

    # --- Step 2: Create the master data table ---
    
    # Merge dependencies and features. Because both have a 'Title' column, pandas will
    # add suffixes. 'Title' from dependencies becomes 'Title_dep'.
    merged_df = pd.merge(
        dependencies_df,
        features_df,
        on='epic_id',
        how='inner',
        # suffixes=('_dep', '_feat') 
    )
    
    # Merge the result with initiatives.
    master_df = pd.merge(
        merged_df,
        initiatives_df,
        left_on='initiative_id',
        right_on='initiative_id', # Using exact column name from initiatives_report.csv
        how='inner'
    )
    print(f"Found {len(master_df)} records with a complete Dependency -> Feature -> Initiative chain.")

    if master_df.empty: return print("Could not find any full links. Halting.")

    # Find all features that belong to the relevant initiatives
    relevant_initiative_ids = set(master_df['initiative_id'].unique())
    context_features_df = features_df[features_df['initiative_id'].isin(relevant_initiative_ids)]
    
    # --- Step 3: Prepare nodes and links ---

    # Create a unified list of all items that will appear in the diagram
    all_items = []

    # Add Initiatives
    for _, row in initiatives_df[initiatives_df['initiative_id'].isin(relevant_initiative_ids)].iterrows():
        all_items.append({
            'id': row['initiative_id'],
            'type': 'Initiative',
            'title': row['initiative_title']
        })

    # Add Features (all features from the relevant initiatives)
    for _, row in context_features_df.iterrows():
        all_items.append({
            'id': row['epic_id'],
            'type': 'Feature',
            'title': row['epic_title']
        })
        
    # Add Dependencies (only the ones that started our chain)
    for _, row in master_df.iterrows():
        all_items.append({
            'id': row['dependency_id'],
            'type': 'Dependency',
            'title': row['dependency_title'] # Using the generated column name
        })

    # Create the final, de-duplicated list of nodes
    all_nodes = pd.DataFrame(all_items).drop_duplicates(subset=['id', 'type']).reset_index(drop=True)
    all_nodes['label'] = all_nodes['type'] + ": " + all_nodes['title'].fillna('No Title')
    all_nodes['hover_text'] = all_nodes.apply(lambda row: f"{row['type']} ID: {row['id']}<br>Title: {row['title']}", axis=1)
    
    # Create the mapping from ID to its numerical index for Plotly
    node_map = {row['id']: i for i, row in all_nodes.iterrows()}
    
    color_map = {'Initiative': '#007bff', 'Feature': '#28a745', 'Dependency': '#ffc107'}
    node_colors = [color_map.get(node_type, '#808080') for node_type in all_nodes['type']]

    # Create links
    links = []
    # Dependency -> Feature links
    for _, row in master_df.iterrows():
        links.append({'source': node_map[row['dependency_id']], 'target': node_map[row['epic_id']]})
    
    # Feature -> Initiative links
    for _, row in context_features_df.iterrows():
        if pd.notna(row['initiative_id']) and row['initiative_id'] in relevant_initiative_ids:
            links.append({'source': node_map[row['epic_id']], 'target': node_map[row['initiative_id']]})

    print(f"\nTotal Nodes: {len(all_nodes)}, Total Links: {len(links)}")

    # --- Step 4: Create and save the Sankey Diagram ---
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 15, thickness = 20,
            label = all_nodes['label'].tolist(),
            customdata = all_nodes['hover_text'].tolist(),
            hovertemplate='<b>%{customdata}</b><extra></extra>',
            color = node_colors
        ),
        link = dict(
            source = [l['source'] for l in links],
            target = [l['target'] for l in links],
            value = [1] * len(links)
        )
    )])
    fig.update_layout(title_text="Prioritization Context: Dependency-Driven Initiatives and All Their Features", font_size=12)
    
    output_filename = output_path / 'sankey_prioritization_context.html'
    fig.write_html(str(output_filename))
    print(f"\n--- SUCCESS! ---")
    print(f"Sankey diagram saved to: {output_filename}")

if __name__ == '__main__':
    create_prioritization_sankey()
