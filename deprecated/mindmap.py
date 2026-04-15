import pandas as pd
import networkx as nx
from pyvis.network import Network
from pathlib import Path

def create_interactive_relationship_map():
    """
    Reads the reports and generates a robust interactive HTML mind map,
    providing detailed debugging for missing relationships.
    """
    print("--- Starting Interactive Map Generation ---")

    data_path = Path(__file__).resolve().parent.parent / 'data'
    output_path = Path(__file__).resolve().parent.parent / 'output'
    output_path.mkdir(exist_ok=True)

    # --- Step 1: Load the data ---
    try:
        initiatives_df = pd.read_csv(data_path / 'initiatives_report.csv') 
        features_df = pd.read_csv(data_path / 'epic_features_report.csv')
        dependencies_df = pd.read_csv(data_path / 'dependencies_report.csv')
        print("Successfully loaded all three report files.")
    except FileNotFoundError as e:
        print(f"Error: Could not find a required data file. {e}")
        return

    # =========================================================================
    # === THE MAIN CHANGE: We initialize the pyvis Network directly ===
    # We will no longer use the 'networkx' library at all.
    # =========================================================================
    net = Network(height="900px", width="100%", notebook=False, directed=True)

    # --- Step 3: Add nodes and edges with enhanced debugging ---

    # Add Initiatives
    for _, row in initiatives_df.iterrows():
        if pd.notna(row['initiative_id']):
            node_id = f"I{int(row['initiative_id'])}"
            title = row.get('initivate_title', 'No Title')
            net.add_node(node_id, label=title, shape='box', color='#007bff', title=f"Initiative: {title}")

    # Add Features and link them to Initiatives
    for _, row in features_df.iterrows():
        if pd.notna(row['epic_id']):
            node_id = f"F{int(row['epic_id'])}"
            title = row.get('epic_title', 'No Title')
            net.add_node(node_id, label=title, shape='ellipse', color='#28a745', title=f"Feature: {title}")
            
            if pd.notna(row['initiative_id']):
                parent_initiative_id = f"I{int(row['initiative_id'])}"
                net.add_edge(source=node_id, to=parent_initiative_id)

    # Add Dependencies and link them to Features
    for _, row in dependencies_df.iterrows():
        if pd.notna(row['dependency_id']):
            node_id = f"D{int(row['dependency_id'])}"
            title = row.get('dependency_title', 'No Title')
            net.add_node(node_id, label=title, shape='diamond', color='#dc3545', title=f"Dependency: {title}")

            if pd.notna(row['epic_id']):
                parent_feature_id = f"F{int(row['epic_id'])}"
                net.add_edge(source=node_id, to=parent_feature_id)

    # --- Step 3: Customize physics and Generate the HTML file ---
    print("\n--- Graph Construction Complete ---")
    print("All nodes and edges have been added directly to the pyvis network.")
    
    net.set_options("""
    var options = { "physics": { "solver": "barnesHut", "barnesHut": { "springConstant": 0.05, "nodeDistance": 350 } } }
    """)
    
    try:
        output_filename = output_path / 'final_relationship_map.html'
        net.show(str(output_filename))
        print(f"\n--- SUCCESS! ---")
        print(f"Interactive map saved to: {output_filename}")
        print("You can now open this HTML file in your web browser.")
    except Exception as e:
        print(f"\nAn error occurred during HTML generation: {e}")

if __name__ == '__main__':
    create_interactive_relationship_map()