1. install python with pyenv
- if you don't have administration permissoin, you can't use package and brew to install.
- the Anaplan company block the repo.anandco.com, so miniconda will fail.
- The only way is pyent to install python.
- If you directly install python on this mac, you will face '_lzma' module not found error.
- To fix this error, you need to install xz package maully.
- After installing xz package, you can install python using pyenv.
<code>
mkdir -p ~/local/xz	//Creates a destination folder in your home directory for the new library.
cd /tmp	Navigates to a temporary directory for the download.
curl -O https://tukaani.org/xz/xz-5.4.6.tar.gz	Downloads the source code for the xz library.
tar -xvf xz-5.4.6.tar.gz && cd xz-5.4.6	Extracts the source code and enters the directory.
./configure --prefix=$HOME/local/xz	Configures the build to install into your ~/local/xz folder, not a system folder.
make && make install	Compiles and installs the library into your local folder.
</code>

Step 2: Install Python Using pyenv (Pointing to Your Local Library)
Now we will tell pyenv to install a fresh copy of Python, making sure it knows where to find the xz library you just built.

Command	Description
CFLAGS="-I$HOME/local/xz/include" LDFLAGS="-L$HOME/local/xz/lib" pyenv install 3.11.7	This is the most important command. It tells pyenv to build Python 3.11.7 while looking for libraries in your ~/local/xz folder. This process may take several minutes as it is compiling Python from scratch.
pyenv global 3.11.7	Sets your newly installed Python as the default version for your user account.
pyenv rehash	Updates the pyenv shims to make sure your terminal can find the new Python commands.


Step 3: Verify Your New Python Installation
Close and reopen your terminal to make sure all changes take effect. Then run these commands:

Command	Expected Output
which python3	/Users/zi.wang/.pyenv/shims/python3 (Confirms you're using the pyenv version)
python3 --version	Python 3.11.7 (Confirms the new version is active)
python3 -c "import _lzma"	(No output) If this command runs silently with no errors, you have successfully fixed the _lzma issue!


source venv/bin/activate

---------------------------------------------------------------------------------------------------------------

Project Structure:
src/
├── config.py.        
├── api_client.py
├── data_processor.py
└── main.py

config.py: contains the configuration for the API client and data processor. DON'T COMMIT THIS FILE TO GIT.
api_client.py: contains the code for interacting with the Anaplan API. 
data_processor.py: contains the code for processing the data returned by the API.
main.py: contains the main logic for the program.


--------------------------------------------------------------------------------------------------------

1. Conceptual Workflow and Data Flow Graph
This graph describes the "story" of the application—how data moves from one component to another. It focuses on the sequence of events when main.py is executed.

Here is a step-by-step representation of the workflow logic:
(Start)
   |
   V
[ main.py ] -- 1. Starts execution.
   |
   |-- 2. Calls get_align_data() in api_client.
   |
   V
[ api_client.py ] -- 3. Needs credentials.
   |
   |-- 4. Imports URL and TOKEN from config.
   |
   V
[ config.py ] -- 5. Provides credentials.
   |
   V
[ api_client.py ] -- 6. Fetches data from Jira Align API.
   |
   |-- 7. Returns raw data (list of Initiatives/Epics).
   |
   V
[ main.py ] -- 8. Receives raw data.
   |
   |-- 9. Calls process_and_join_data() with the raw data.
   |
   V
[ data_processor.py ] -- 10. Cleans, renames, and joins data into a pandas DataFrame.
   |
   |-- 11. Returns the processed DataFrame.
   |
   V
[ main.py ] -- 12. Receives the final DataFrame.
   |
   |-- 13. Calls save_to_csv() to store the result.
   |
   V
[ data_processor.py ] -- 14. Writes the DataFrame to "jira_align_dashboard_data.csv".
   |
   V
 (End)

------------------
https://anaplan.jiraalign.com/rest/align/api/docs/index.html
----------------------



