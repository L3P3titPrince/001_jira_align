# 005_test_idea_programid.py
#
# Tests whether the /Ideas list endpoint returns 'programId'
# when explicitly requested via $select (Strategy 1).
#
# Run from the src/ directory:
#   python 005_test_idea_programid.py

import json
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / 'src'))
import api_client


def test_idea_programid_in_select():
    """
    Fetches a small sample of Ideas requesting 'programId' in $select,
    then checks whether the field is present and non-null in the response.
    """
    print("=" * 60)
    print("TEST: Does /Ideas return 'programId' via $select?")
    print("=" * 60)

    # Request a small page (5 ideas) with programId included
    select_fields = "id,title,status,ownerId,groupId,programId"

    sample = api_client.get_paged_align_data(
        endpoint="/rest/align/api/2/Ideas",
        select=select_fields
    )

    if not sample:
        print("\nFAIL: API returned no ideas at all. Check credentials / endpoint.")
        return

    # Limit display to first 5 records
    sample = sample[:5]

    print(f"\nReceived {len(sample)} sample idea(s). Full raw records:")
    for record in sample:
        print(json.dumps(record, indent=2))

    # --- Verification checks ---
    print("\n--- Verification ---")

    has_program_id = all('programId' in record for record in sample)
    has_non_null   = any(record.get('programId') is not None for record in sample)

    if has_program_id and has_non_null:
        print("PASS: 'programId' is present and non-null in the response.")
        print("      Strategy 1 will work — add programId to idea_extract.py.")
    elif has_program_id:
        print("PARTIAL: 'programId' key exists but is null for all sampled ideas.")
        print("         The field may not be populated for these records.")
        print("         Try a larger sample or check a known idea in the UI.")
    else:
        print("FAIL: 'programId' is NOT in the response.")
        print("      Strategy 1 will not work — use Strategy 2 (individual fetch).")

    # Show a quick summary table
    print("\n--- programId values in sample ---")
    print(f"{'idea_id':<10} {'programId':<15} {'title'}")
    print("-" * 60)
    for r in sample:
        print(f"{r.get('id', '?'):<10} {str(r.get('programId', 'MISSING')):<15} {r.get('title', '')[:40]}")


if __name__ == "__main__":
    test_idea_programid_in_select()
