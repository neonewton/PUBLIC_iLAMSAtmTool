

# MacOS
python3.13 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install --upgrade pip
streamlit run "1_Elentra_iLAMS_atm_tool_V6/home.py"

# Windows
python3.13 -m venv venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install --upgrade pip
streamlit run "1_Elentra_iLAMS_atm_tool_V6/home.py"


# NOTES
# Create virtual environment (replace `venv` with your preferred folder)
python3.13 -m venv venv

# Go to Directory
cd ./1_Elentra_iLAMS_atm_tool_V6

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Check Python Version
python3 -V

# Install Required Packages
pip install -r requirements.txt
pip install --upgrade pip

# Python Interpreter
Make sure your script uses the correct Python interpreter path:
#!/usr/local/bin/python3
In VS Code, use ⇧ + ⌘ + P → “Python: Select Interpreter” and choose Python 3.13 manually.

# Open UI
streamlit run "1_Elentra_iLAMS_atm_tool_V6/home.py"
streamlit run "home.py"

