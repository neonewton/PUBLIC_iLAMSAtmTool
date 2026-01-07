# iLAMS–Elentra Automation Tool (Local Setup)

This guide helps first-time users run the **iLAMS–Elentra Automation Tool** locally on **MacOS or Windows**, assuming Python and Chrome are available.

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

---

## 📥 Prerequisites

Before starting, download and install the following:
- **Windows:**  : win64 **or**
- **MacOS:** : mac-arm64
- **Python at least 3.11 or newer**  
- **Google Chrome & Chrome WebDriver**  
- **This GitHub zipped Project files**

---

## 📂 Recommended Folder Location (Optional)

> #### **Tip:**  
> - Open Terminal (macOS) or PowerShell (Windows) from this directory before running any commands.
> - For consistency and fewer path issues, place the project under:
> - ~/Documents/GitHub/PUBLIC_AutoTool-LAMS-Elentra/1_Elentra_iLAMS_atm_tool_V6.
> - For webdriver directory, place it together with the downloaded project folder.
> - Place the folder Chromedriver folder under "Webdrivers" in the "1_Elentra_iLAMS_atm_tool_V6" folder.

---

## ▶️ How to Run (First Time)

### Step 1: Open a terminal

- **macOS:** `Terminal.app`
- **Windows:** 'Terminal'

---

### Step 2: Navigate to the project directory

Example:

```bash
cd ~/Documents/GitHub/PUBLIC_AutoTool-LAMS-Elentra/_Elentra_iLAMS_atm_tool_V6

```
---
### Step 3: Setup & Run
- Copy and paste the following commands from **1_commands_macos.txt** or **1_commands_windows.txt**
---

### 🔁 **Step 4: Subsequent Runs** 🔁

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


