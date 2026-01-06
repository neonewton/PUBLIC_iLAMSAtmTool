# Create virtual environment (replace `venv` with your preferred folder)
python3.13 -m venv venv

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


"""
# Ensure you have started Chrome with:
r"""
MAC:
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile"
then
curl http://127.0.0.1:9222/json
WINDOWS:
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  --remote-debugging-port=9222 `
  --user-data-dir="C:\Users\Neone\chrome-debug-profile"
then
curl http://127.0.0.1:9222/json

"""


streamlit run "1_Elentra_iLAMS_atm_tool_V6/home.py"
streamlit run "home.py"



2️⃣ Create a new virtual environment (do NOT reuse old one)

From your project root:

python3.11 -m venv .venv-build
source .venv-build/bin/activate

---------
Confirm:

python3 --version
# Python 3.11.x


⚠️ This step is mandatory

3️⃣ Reinstall everything cleanly
4️⃣ FULL CLEAN (important)
5️⃣ Rebuild your app

python3.11 -m venv .venv-build
source .venv-build/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

rm -rf build dist *.spec __pycache__
rm -rf dist build *.spec

pyinstaller \
  --windowed \
  --onedir \
  --clean \
  --name "Elentra_iLAMS_atm_tool_V6" \
  --add-data "Home.py:." \
  --add-data "pages:pages" \
  --add-data "core:core" \
  --add-data "requirements.txt:." \
  launcher.py

./dist/Elentra_iLAMS_atm_tool_V6
  