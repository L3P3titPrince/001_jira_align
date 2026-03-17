import requests
import json
import config  # Imports JIRA_ALIGN_URL and API_TOKEN

# --- Configuration ---
# Replace with your Jira Align instance URL (e.g., "https://mycompany.jiraalign.com")
JIRA_ALIGN_URL = "https://anaplan.jiraalign.com/"

# Replace with the API token you generated from your Jira Align profile
API_TOKEN = "user:2017|YD~V+DamZL|t/DmRgb7d]ceRK6<PYgQa4Wj8xj*5"

# This is the specific API endpoint you want to get data from.
# This example fetches Epics. You can find more endpoints in the API documentation.
# See: https://help.jiraalign.com/hc/en-us/articles/360045371954-Getting-started-with-the-REST-API-2-0
ENDPOINT = "/rest/align/api/2/Epics/592"

# --- Do not edit below this line ---

def extract_jira_align_data():
    """
    Connects to the Jira Align API and extracts data from the specified endpoint.
    """
    full_url = JIRA_ALIGN_URL + ENDPOINT
    
    # The API token is sent in the 'Authorization' header with the "Bearer" prefix.
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to: {full_url}")

    try:
        # Make the GET request to the API
        response = requests.get(full_url, headers=headers)
        
        # This will raise an exception if the request returned an error (e.g., 401, 404, 500)
        response.raise_for_status()
        
        # Parse the JSON response from the API
        data = response.json()
        
        print("Successfully extracted data.")
        
        # Pretty-print the first item in the response as an example
        if data:
            print("\n--- Example Record ---")
            print(json.dumps(data[0], indent=2))
        else:
            print("The request was successful, but no data was returned from this endpoint.")
            
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Body: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    
    return None


def get_single_feature(feature_id: int):
    """
    Fetches data for a single Feature from the Jira Align API.

    Args:
        feature_id: The ID of the Feature to retrieve.
    """
    endpoint = f"/rest/align/api/2/Features/{feature_id}"
    full_url = config.JIRA_ALIGN_URL + endpoint
    
    headers = {
        "Authorization": f"Bearer {config.API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"Sending request to: {full_url}")

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (401, 404, etc.)

        feature_data = response.json()
        
        print("\n--- Successfully Extracted Feature Data ---")
        # Pretty-print the full JSON object
        print(json.dumps(feature_data, indent=2))
        
        return feature_data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response Body: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    
    return None

def extract_single_jira_align_epic():
    """
    Connects to the Jira Align API and extracts data for a single Epic.
    """
    full_url = JIRA_ALIGN_URL + ENDPOINT

    # The API token is sent in the 'Authorization' header with the "Bearer" prefix.
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    print(f"Sending request to: {full_url}")

    try:
        # Make the GET request to the API
        response = requests.get(full_url, headers=headers)

        # This will raise an exception if the request returned an error (e.g., 401, 404, 500)
        response.raise_for_status()

        # The response for a single item is a JSON object, not a list.
        data = response.json()

        print("\n--- Successfully Extracted Epic Data ---")
        # Pretty-print the entire object.
        print(json.dumps(data, indent=2))
        
        return data

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        # A '401 Unauthorized' error here means your API_TOKEN is still incorrect or has expired.
        print(f"Response Body: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
    
    return None

if __name__ == "__main__":
    # extracted_data = extract_jira_align_data()
    # extracted_data = extract_single_jira_align_epic()

    # if extracted_data:
    #     # You can now process the 'extracted_data' list as needed.
    #     # For example, print the number of items received:
    #     print(f"\nTotal records received: {len(extracted_data)}")


    target_feature_id = 10732
    feature_information = get_single_feature(target_feature_id)

    if feature_information:
        # Example of how to use the extracted data
        feature_name = feature_information.get('name')
        feature_state = feature_information.get('state')
        parent_epic_id = feature_information.get('epicId')

        print(f"\nSuccessfully processed Feature '{feature_name}' (State: {feature_state}).")
        if parent_epic_id:
            print(f"This Feature belongs to Epic with ID: {parent_epic_id}")

