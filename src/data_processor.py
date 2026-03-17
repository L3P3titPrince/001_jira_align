# data_processor.py
#
# Handles data transformations and saving.

import pandas as pd
from pathlib import Path  # NEW: Import the Path object from pathlib

def save_to_csv(df: pd.DataFrame, filename: str, column_mapping: dict = None):
    """
    Saves a pandas DataFrame to a CSV file inside a 'data' folder
    at the project root, with optional column renaming.

    Args:
        df: The pandas DataFrame to save.
        filename: The base name of the output CSV file (e.g., "epics_report.csv").
        column_mapping (optional): A dictionary to rename columns.
    """
    if df.empty:
        print(f"Skipping save for '{filename}' because the DataFrame is empty.")
        return

    # === NEW: LOGIC TO DEFINE THE SAVE LOCATION ===

    # 1. Get the path of the project's root directory.
    # Path(__file__) is the path to this current file (data_processor.py).
    # .resolve() makes it an absolute path.
    # .parent gets the directory of the file (src/).
    # .parent again gets the parent of src/ (the project root).
    project_root = Path(__file__).resolve().parent.parent
    
    # 2. Define the path to the 'data' directory.
    data_dir = project_root / 'data'

    # 3. Create the 'data' directory if it doesn't already exist.
    # exist_ok=True means it won't raise an error if the folder is already there.
    data_dir.mkdir(exist_ok=True)
    
    # 4. Construct the full, final path for the CSV file.
    full_path = data_dir / filename
    
    # ===============================================

    # Create a copy to avoid modifying the original DataFrame
    df_to_save = df.copy()

    if column_mapping:
        df_to_save.rename(columns=column_mapping, inplace=True)
        print(f"Renamed columns for '{filename}'.")

    try:
        # Use the new full_path to save the file
        df_to_save.to_csv(full_path, index=False)
        # Update the print statement to show the new location
        print(f"Successfully saved data to '{full_path}'.")
    except Exception as e:
        print(f"Error saving to CSV '{full_path}': {e}")
