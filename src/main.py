# main.py
#
# The main entrypoint for the application.

import api_client
import data_processor

def main():
    """
    Orchestrates the data extraction, processing, and saving pipeline.
    """
    print("--- Starting Jira Align Data Extraction ---")
    
    # 1. Extract data using the API client
    initiatives = api_client.get_align_data("/rest/align/api/2/Initiatives")
    epics = api_client.get_align_data("/rest/align/api/2/Epics")
    
    # 2. Process the data
    dashboard_data = data_processor.process_and_join_data(initiatives, epics)
    
    # 3. Save the final dataset
    if not dashboard_data.empty:
        data_processor.save_to_csv(dashboard_data, "jira_align_dashboard_data.csv")
        print("\n--- First 5 rows of your new dataset ---")
        print(dashboard_data.head())

    print("\n--- Pipeline Finished ---")


if __name__ == "__main__":
    # Ensure you have installed the required libraries:
    # pip install requests pandas
    main()
