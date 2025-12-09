# Create virtual environment (replace `venv` with your preferred folder)
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Check Python Version
python3 -V

# Install Required Packages
pip install -r requirements.txt

# Python Interpreter
Make sure your script uses the correct Python interpreter path:
#!/usr/local/bin/python3
In VS Code, use ⇧ + ⌘ + P → “Python: Select Interpreter” and choose Python 3.13 manually.

⚠️ Avoid using:
#!/usr/bin/env python3


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

iLAMS_admin_tool/
├─ app.py
├─ core/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ selenium_utils.py
│  ├─ elentra_link_upload.py
│  ├─ excel_generation.py
│  ├─ excel_combine.py
│  ├─ search_users.py
│  └─ bulk_course_archive.py
└─ pages/
   ├─ 1_Elentra_Link_Upload.py
   ├─ 2_User_Excel_Generation.py
   ├─ 3_User_Excel_Combination.py
   ├─ 4_iLAMS_Search_Users.py
   └─ 5_iLAMS_Bulk_Courses_Archive.py
