# iLAMS–Elentra Automation Tool (Local Setup)

This guide helps first-time users run the **iLAMS–Elentra Automation Tool** locally on **MacOS or Windows**, assuming Python and Chrome are available.

---

## 📥 Prerequisites

Before starting, download and install the following:

- **Python 3.13**  
  https://www.python.org/downloads/

- **Google Chrome & Chrome WebDriver**  
  https://googlechromelabs.github.io/chrome-for-testing/

- **Project files**
  - Download the relevant Python packages and Chrome WebDriver from:
    - `2_Windows/` **or**
    - `2_MacOS/`

---

## 📂 Recommended Folder Location (Strongly Advised)

For consistency and fewer path issues, place the project under:
~/Documents/GitHub/PUBLIC_AutoTool-LAMS-Elentra/1_Elentra_iLAMS_atm_tool_V6


> **Tip:**  
> Open Terminal (macOS) or PowerShell (Windows) from this directory before running any commands.

---

## ▶️ How to Run (First Time)

### Step 1: Open a terminal

- **macOS:** `Terminal.app`
- **Windows:** `PowerShell`

---

### Step 2: Navigate to the project directory

Example:

```bash
cd ~/Documents/GitHub/PUBLIC_AutoTool-LAMS-Elentra/_Elentra_iLAMS_atm_tool_V6

```
---
## Step 3: Setup & Run

### macOS Setup & Run

Copy and paste the following commands from **1_commands_macos.txt**, or run directly:

```bash
python3.13 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

streamlit run Home.py
```

### Windows Setup & Run

Copy and paste the following commands from **1_commands_windows.txt**, or run directly:
```bash
py -3.13 -m venv venv
.\venv\Scripts\Activate

python -m pip install --upgrade pip
pip install -r requirements.txt

streamlit run Home.py
```
---

## Step 4: Subsequent Runs

After the first setup, you only need to:

### MacOS
```bash
source venv/bin/activate
streamlit run Home.py
```

### Windows
```bash
.\venv\Scripts\Activate.ps1
streamlit run Home.py
```
---

### 🌐 Useful Links

GitHub Repository
https://github.com/neonewton/PUBLIC_AutoTool-LAMS-Elentra

Streamlit Cloud (Bulk Excel Generation)
https://autotool-ilams-elentrav2.streamlit.app/

Python (Official Download)
https://www.python.org/downloads/

Chrome & Chrome WebDriver
https://googlechromelabs.github.io/chrome-for-testing/

