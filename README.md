# iLAMS–Elentra Automation Tool (Local Setup)

This guide helps first-time users run the **iLAMS–Elentra Automation Tool** locally on **MacOS or Windows**, assuming Python and Chrome are available.

---

## 📥 Prerequisites

Before starting, download and install the following:

- **Python 3.13**  
  https://www.python.org/downloads/

- **Google Chrome & Chrome WebDriver**  
- **Project files**
Download the relevant Python packages and Chrome WebDriver from:
https://googlechromelabs.github.io/chrome-for-testing/
  - `2_Windows/` : win64 **or**
  - `2_MacOS/` : mac-arm64

For webdriver directory, place it together with the downloaded project folder. 
Place the folder "Chromedriver-..." together with "1_Elentra_iLAMS_atm_tool_V6" under "Webdrivers"
---

## 📂 Recommended Folder Location (Optional)

> **Tip:**  
> Open Terminal (macOS) or PowerShell (Windows) from this directory before running any commands.
> For consistency and fewer path issues, place the project under:
> ~/Documents/GitHub/PUBLIC_AutoTool-LAMS-Elentra/1_Elentra_iLAMS_atm_tool_V6

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

Copy and paste the following commands from **1_commands_macos.txt**, or **1_commands_windows.txt**, or run directly:

---

## Step 4: Subsequent Runs

After the first setup, you only need to:

### MacOS
```bash
### Open the folder "1_Elentra_iLAMS_atm_tool_V6" in Terminal ###
source venv/bin/activate
streamlit run Home.py
```

### Windows
```bash
### Open the folder "1_Elentra_iLAMS_atm_tool_V6" in Terminal ###
venv\Scripts\Activate
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

