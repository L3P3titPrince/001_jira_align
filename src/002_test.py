# In main.py
import api_client
import data_processor

def extract_specific_epics_by_id_corrected():
    """
    Extracts a specific list of Epics by their IDs using the supported
    '(id eq ... or id eq ...)' filter format.
    """
    print("--- Starting extraction of specific Epics by ID (Corrected Method) ---")

    # 1. DEFINE YOUR LIST OF IDs
    epic_ids_to_extract = [589, 591, 592]

    # 2. CONSTRUCT THE CORRECT ODATA FILTER
    # Create a list of individual 'id eq ...' clauses
    or_clauses = [f"id eq {epic_id}" for epic_id in epic_ids_to_extract]
    
    # Join the clauses with ' or ' and wrap the whole thing in parentheses
    my_filters = f"({' or '.join(or_clauses)})"
    
    # Specify the fields you want to retrieve
    my_fields = "id,name,state,ownerId,programId,programIncrementId"

    print(f"Using filter: {my_filters}")

    # 3. EXECUTE THE API CALL
    specific_epics = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Epics",
        filters=my_filters,
        select=my_fields
    )

    if specific_epics:
        print(f"\nSuccessfully extracted {len(specific_epics)} Epics.")
        
        # Process the data as usual
        epics_df = data_processor.pd.DataFrame(specific_epics)
        data_processor.save_to_csv(epics_df, "specific_epics_list_corrected.csv")
        print("\nExtracted Epic data:")
        print(epics_df.head())
    else:
        print("\nNo Epics found matching the provided IDs, or an error occurred.")

if __name__ == "__main__":
    extract_specific_epics_by_id_corrected()
