import pandas as pd
from pathlib import Path

def prepare_sankey_data():
    """
    This function is responsible for all data loading, merging, and preparation.
    It now also saves the intermediate master data table to a CSV file.
    It returns a tuple of lists ready for plotting with Plotly.
    """
    print("--- Data Loader: Loading and Preparing Data ---")
    data_path = Path(__file__).resolve().parent.parent / 'data'
    output_path = Path(__file__).resolve().parent.parent / 'output'
    output_path.mkdir(exist_ok=True)

    # --- Step 1: Load the data ---
    try:
        initiatives_df = pd.read_csv(data_path / 'initiatives_report.csv')
        features_df = pd.read_csv(data_path / 'epic_features_report.csv')
        dependencies_df = pd.read_csv(data_path / 'dependencies_report.csv')
    except Exception as e:
        print(f"Error loading files: {e}")
        return None

    # --- Step 2: Create the master data table by joining ---
    merged_df = pd.merge(dependencies_df, features_df, on='epic_id', how='inner', suffixes=('_dep', '_feat'))
    master_df = pd.merge(merged_df, initiatives_df, left_on='initiative_id', right_on='initiative_id', how='inner',suffixes=('_dep', '_init'))

    if master_df.empty:
        print("Could not find any full Dependency -> Feature -> Initiative chains.")
        return None
    
    print(f"Successfully created a master table with {len(master_df)} fully linked records.")

    # =========================================================================
    # === NEW FEATURE: Save the master DataFrame to a CSV file ===
    # =========================================================================
    try:
        master_csv_path = output_path / 'master_data_table.csv'
        master_df.to_csv(master_csv_path, index=False)
        print(f"Successfully saved the joined master table to: {master_csv_path}")
    except Exception as e:
        print(f"Warning: Could not save the master data table. Error: {e}")
    # =========================================================================

    # # --- The rest of the script continues as before ---

    # relevant_initiative_ids = set(master_df['intiative_id'].unique())
    # context_features_df = features_df[features_df['initiative_ID'].isin(relevant_initiative_ids)]

    # # --- Step 3: Prepare the nodes list ---
    # # (This section is unchanged)
    # dep_nodes = master_df[['dependency_id', 'Title_dep']].rename(columns={'dependency_id': 'id', 'Title_dep': 'title'})
    # dep_nodes['type'] = 'Dependency'
    # feat_nodes = context_features_df[['epic_id', 'Title']].rename(columns={'epic_id': 'id', 'Title': 'title'})
    # feat_nodes['type'] = 'Feature'
    # init_nodes_df = initiatives_df[initiatives_df['intiative_id'].isin(relevant_initiative_ids)]
    # init_nodes = init_nodes_df[['intiative_id', 'Title']].rename(columns={'intiative_id': 'id', 'Title': 'title'})
    # init_nodes['type'] = 'Initiative'

    # all_nodes = pd.concat([dep_nodes, feat_nodes, init_nodes]).drop_duplicates(subset=['id', 'type']).reset_index(drop=True)
    # all_nodes['label'] = all_nodes['type'] + ": " + all_nodes['title'].fillna('No Title')
    # all_nodes['hover_text'] = all_nodes.apply(lambda row: f"{row['type']} ID: {row['id']}<br>Title: {row['title']}", axis=1)

    # node_map = {row['id']: i for i, row in all_nodes.iterrows()}
    # color_map = {'Initiative': '#007bff', 'Feature': '#28a745', 'Dependency': '#ffc107'}

    # # --- Step 4: Prepare the links list ---
    # # (This section is unchanged)
    # links = []
    # for _, row in master_df.iterrows():
    #     links.append({'source': node_map[row['dependency_id']], 'target': node_map[row['epic_id']]})
    # for _, row in context_features_df.iterrows():
    #     if pd.notna(row['initiative_ID']) and row['initiative_ID'] in relevant_initiative_ids:
    #         links.append({'source': node_map[row['epic_id']], 'target': node_map[row['initiative_ID']]})

    # # --- Step 5: Prepare final lists for Plotly ---
    # # (This section is unchanged)
    # node_labels = all_nodes['label'].tolist()
    # node_colors = [color_map.get(node_type, '#808080') for node_type in all_nodes['type']]
    # node_hovertext = all_nodes['hover_text'].tolist()
    # link_sources = [link['source'] for link in links]
    # link_targets = [link['target'] for link in links]

    # print(f"Data preparation complete. Found {len(all_nodes)} nodes and {len(links)} links for visualization.")
    
    # return node_labels, node_colors, node_hovertext, link_sources, link_targets

    return None

if __name__ == '__main__':
    prepare_sankey_data()