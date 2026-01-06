Download the relevant python pkg and chrome webdriver from either the "2_Windows" or "2_MacOS" files
Open terminal.app or powershell.exe
Copy and paste the commands from "1_commands_macos.txt" or "1_commands_windows.txt'

Strong advise to paste under 
>>Username
>>Documents
>>GitHub
>>PUBLIC_iLAMSAtmTool
>>1_Elentra_iLAMS_atm_tool_V6


Other Essential Links:
GitHub Respoitory: https://github.com/neonewton/PUBLIC_AutoTool-LAMS-Elentra
Streamlit Cloud for Bulk Excel Generation: https://autotool-ilams-elentrav2.streamlit.app/
Python.org, download version 3.13: https://www.python.org/downloads/ 
Chrome & Chrome Webdriver: https://googlechromelabs.github.io/chrome-for-testing/

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

