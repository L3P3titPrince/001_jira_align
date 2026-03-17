# api_client.py
#
# Handles all communication with the Jira Align REST API.

import requests
import config  # Import configuration variables

def get_align_data(endpoint: str) -> list:
    """
    Connects to the Jira Align API and extracts data from a specific endpoint.

    Args:
        endpoint: The API endpoint to fetch data from (e.g., "/rest/align/api/2/Epics").

    Returns:
        A list of dictionaries, where each dictionary is a record.
        Returns an empty list on failure.
    """
    full_url = config.JIRA_ALIGN_URL + endpoint
    headers = {
        "Authorization": f"Bearer {config.API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to: {full_url}...")

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        print(f"Successfully extracted {len(data)} records from {endpoint}.")
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Body: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    
    return []



def get_paged_align_data(endpoint: str, filters: str = "", select: str = "") -> list:
    """
    Extracts all data from a Jira Align endpoint, handling pagination and filtering.

    Args:
        endpoint: The API endpoint (e.g., "/rest/align/api/2/Epics").
        filters: An OData filter string (e.g., "state eq 'In Progress'").
        select: A comma-separated list of fields to select.

    Returns:
        A list of all records matching the query. Returns an empty list on failure.
    """
    all_records = []
    skip = 0
    top = 100  # The number of items to get per page

    headers = {
        "Authorization": f"Bearer {config.API_TOKEN}",
        "Content-Type": "application/json"
    }

    while True:
        # Build the URL with OData parameters for pagination, filtering, and selection
        params = {
            '$top': top,
            '$skip': skip
        }
        if filters:
            params['$filter'] = filters
        if select:
            params['$select'] = select

        full_url = config.JIRA_ALIGN_URL + endpoint
        print(f"Fetching page: top={top}, skip={skip} from {endpoint}")

        try:
            response = requests.get(full_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            
            page_data = response.json()
            if not page_data:
                # This is the exit condition: the API returned an empty list, so we're done.
                break
            
            all_records.extend(page_data)
            skip += top  # Move to the next page for the next loop iteration

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response Body: {response.text}")
            break # Exit the loop on error
        except requests.exceptions.RequestException as err:
            print(f"An error occurred: {err}")
            break # Exit the loop on error
            
    print(f"Total records extracted from this endpoint: {len(all_records)}")
    return all_records
