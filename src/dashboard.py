# dashboard.py

import dash
from dash import dcc, html, Input, Output
import pandas as pd

# --- Load your data ---
# This assumes the script is run from the 'src' directory
try:
    epics_df = pd.read_csv('../data/epics_report.csv')
    features_df = pd.read_csv('../data/features_report.csv')
    dependencies_df = pd.read_csv('../data/dependencies_report.csv')
except FileNotFoundError:
    print("Error: Make sure you have run the extraction and the CSV files exist in the 'data' folder.")
    exit()

# --- Initialize the Dash App ---
app = dash.Dash(__name__)

# --- Define the App Layout ---
app.layout = html.Div(style={'fontFamily': 'sans-serif'}, children=[
    html.H1('Jira Align Relational Dashboard'),

    html.H3('Select an Epic'),
    dcc.Dropdown(
        options=[{'label': row['Initiative_Title'], 'value': row['Initiative_ID']} for index, row in epics_df.iterrows()],
        id='epic-dropdown'
    ),

    html.Hr(),

    html.H3('Child Features for Selected Epic'),
    html.Div(id='features-table-container'),

    html.H3('Dependencies for those Features'),
    html.Div(id='dependencies-table-container')
])

# --- Define the Interactivity (Callbacks) ---

# This callback updates the Features table when an Epic is selected
@app.callback(
    Output('features-table-container', 'children'),
    Input('epic-dropdown', 'value')
)
def update_features_table(selected_epic_id):
    if selected_epic_id is None:
        return "Please select an Epic to see its features."

    # Filter the features DataFrame based on the selected Epic
    filtered_features = features_df[features_df['Intiative_ID'] == selected_epic_id]

    if filtered_features.empty:
        return "No child features found for this Epic."

    # Return a Dash DataTable component
    return dash.dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in filtered_features.columns],
        data=filtered_features.to_dict('records'),
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
    )

# You can add a second callback here to update the dependencies table based on the filtered features...

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050) # Running on a different port
