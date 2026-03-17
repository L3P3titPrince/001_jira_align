# At the very top of app.py

import warnings
from urllib3.exceptions import NotOpenSSLWarning

# This line tells Python: "If you see a warning of the type NotOpenSSLWarning,
# just ignore it and don't print it to the console."
warnings.filterwarnings("ignore", category=NotOpenSSLWarning)

# In a new file, e.g., 'app.py'
# At the top of app.py
from flask import Flask, request, jsonify, render_template
from epic_extract_01 import run_extraction_pipeline

app = Flask(__name__)


# =========================================================================
# === NEW FUNCTION TO HANDLE THE ROOT URL ===
#
# This function will be called when a user navigates to http://127.0.0.1:5000/
# It handles GET requests, which is what a browser sends.
# =========================================================================
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
# def index():
#     # Return a simple, helpful HTML message.
#     # You could also return JSON if you prefer.
#     return """
#     <h1>Jira Align Extraction API</h1>
#     <p>Welcome! This is the API server for extracting Epic data from Jira Align.</p>
#     <p>This endpoint (/) is for information only.</p>
#     <p>To extract data, please send a <strong>POST</strong> request to the <strong>/extract</strong> endpoint with a JSON body containing 'programs' and 'releases' keys.</p>
#     <p>Example using curl:</p>
#     <pre><code>
#     curl -X POST http://127.0.0.1:5000/extract \\
#     -H "Content-Type: application/json" \\
#     -d '{"programs": [72, 79], "releases": [54, 55]}'
#     </code></pre>
#     """


# =========================================================================
# This is your existing endpoint, which is working correctly.
# No changes are needed here.
# =========================================================================
@app.route('/extract', methods=['POST'])
def extract_epics_endpoint():
    # Get program and release IDs from the UI's request
    data = request.get_json()
    program_ids = data.get('programs')
    release_ids = data.get('releases')

    if not program_ids or not release_ids:
        return jsonify({"error": "Missing 'programs' or 'releases' in request body"}), 400

    # Call your extraction engine directly
    results_dataframe = run_extraction_pipeline(program_ids, release_ids)

    if results_dataframe.empty:
        return jsonify({"message": "No data found for the specified filters."})
    else:
        # Convert the DataFrame to JSON and send it back to the UI
        return jsonify(results_dataframe.to_dict(orient='records'))

