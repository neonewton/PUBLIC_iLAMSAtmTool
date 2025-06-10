#!/usr/local/bin/python3

"""
pip3 install pandas xlwt
"""

import sys
import os
if os.name == "nt":        # Windows
    os.system("cls")
else:                      # Linux / macOS
    os.system("clear")

import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
import xlwt
from datetime import datetime
from tkinter import ttk  # <-- for Notebook
from tkinter.scrolledtext import ScrolledText

# --- Constants ---
STUDENT_HEADERS = ["* login", "* organisation", "* roles"]
STAFF_HEADERS   = ["* login", "* organisation", "* roles", "* add to lessons [yes/no]"]

# --- Helper Functions ---
def parse_emails(text):
    """
    Parse multi-line or comma-separated emails into a clean list.
    """
    emails = []
    for line in text.splitlines():
        for part in line.split(','):
            email = part.strip()
            if email:
                emails.append(email)
    return emails


def save_xls(folder, filename, headers, rows):
    """
    Write rows (list of lists) with headers (list) to an XLS file in the given folder via xlwt.
    """
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')
    # write headers
    for col, h in enumerate(headers):
        ws.write(0, col, h)
    # write data rows
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            ws.write(r, c, val)
    path = os.path.join(folder, filename)
    wb.save(path)
    return path

# --- Build Functions ---
def build_student_file(folder, course_name, course_id, emails):
    """
    Generate a single student-list .xls file in `folder`.
    """
    today = datetime.now().strftime("%d%m%y")
    rows = [[email, course_id, "Learner"] for email in emails]
    fname = f"{course_name}_CID{course_id}_{today}.xls"
    return save_xls(folder, fname, STUDENT_HEADERS, rows)


def build_staff_files(folder, department, course_id, emails):
    """
    Generate one staff-list .xls file per email in `folder`.
    """
    today = datetime.now().strftime("%d%m%y")
    files = []
    for email in emails:
        rows = [[email, course_id, "Monitor", "Yes"]]
        fname = f"{department}_{email}_{today}.xls"
        files.append(save_xls(folder, fname, STAFF_HEADERS, rows))
    return files

# --- Callbacks ---
def select_folder():
    """Prompt user to pick an output directory."""
    folder = filedialog.askdirectory(initialdir=save_dir_var.get())
    if folder:
        save_dir_var.set(folder)


def run():
    mode = mode_var.get()
    emails = parse_emails(email_text.get('1.0', 'end'))
    cid = course_id_text.get('1.0', 'end').strip()
    folder = save_dir_var.get().strip()

    # Ensure the folder exists (creates it if necessary)
    if folder:
        os.makedirs(folder, exist_ok=True)
    else:
        return messagebox.showerror("Error", "Please select a Save Folder.")

    # Now it definitely exists
    if not os.path.isdir(folder):
        return messagebox.showerror("Error", "Could not create Save Folder.")

    if mode == 'student':
        name = course_name_entry.get().strip()
        if not (emails and cid and name):
            return messagebox.showerror("Error", "Please fill Course Name, Course ID, and Emails.")
        path = build_student_file(folder, name, cid, emails)
        messagebox.showinfo("Success", f"Generated: {path}")
    else:
        dept = dept_entry.get().strip()
        role = role_entry.get().strip()
        if not (emails and cid and dept and role):
            return messagebox.showerror("Error", "Please fill Department, Course ID, Role, and Emails.")
        files = build_staff_files(folder, dept, cid, emails)
        messagebox.showinfo("Success", f"Generated {len(files)} files:\n" + "\n".join(files))


def switch_mode():
    mode = mode_var.get()
    if mode == 'student':
        header_var.set(' | '.join(STUDENT_HEADERS))
        course_name_entry.config(state='normal')
        dept_entry.config(state='disabled')
        role_entry.delete(0, 'end')
        role_entry.insert(0, 'Learner')
    else:
        header_var.set(' | '.join(STAFF_HEADERS))
        # course_name_entry.delete(0, 'end')
        course_name_entry.config(state='disabled')
        dept_entry.config(state='normal')
        role_entry.delete(0, 'end')
        role_entry.insert(0, 'Monitor')

# --- GUI Setup ---
root = tk.Tk()
root.title("LAMS User Import Excel")

mode_var    = tk.StringVar(value='staff')
header_var  = tk.StringVar()
# save_dir_var = tk.StringVar(value=os.getcwd()) # current working directory
today_2 = datetime.now().strftime("%d%m%y")
home = os.path.expanduser("~")
downloads = os.path.join(home, "Downloads", f"LAMS User Import Excel_{today_2}")
save_dir_var = tk.StringVar(value=downloads)


# --- grid layout options ---
row_int = 0
grid_opts = {
    'title_label':          dict(row=row_int+0, column=0, columnspan=3, padx=10, pady=4, sticky='w'),
    'instruction_label':    dict(row=row_int+1, column=0, columnspan=3, padx=10, pady=4, sticky='w'),
    'mode_staff_rb':        dict(row=row_int+2, column=0, padx=8, pady=4, sticky='w'),
    'mode_student_rb':      dict(row=row_int+2, column=1, padx=8, pady=4, sticky='w'),
    'save_label':           dict(row=row_int+3, column=0, sticky='e', padx=4),
    'save_entry':           dict(row=row_int+3, column=1, columnspan=2, sticky='ew', pady=4),
    'browse_btn':           dict(row=row_int+3, column=3, sticky= 'e', padx=4),
    'header_text_label':    dict(row=row_int+4, column=0, sticky='e', padx=4),
    'header_label':         dict(row=row_int+4, column=1, columnspan=2, sticky='w'),
    'emails_label':         dict(row=row_int+5, column=0, sticky='ne', padx=4, pady=4),
    'emails_text':          dict(row=row_int+5, column=1, columnspan=2, sticky='nsew', pady=4),
    'courseid_label':       dict(row=row_int+6, column=0, sticky='ne', padx=4, pady=4),
    'courseid_text':        dict(row=row_int+6, column=1, columnspan=2, sticky='nsew', pady=4),
    'coursename_label':     dict(row=row_int+7, column=0, sticky='e', padx=4),
    'coursename_entry':     dict(row=row_int+7, column=1, columnspan=2, sticky='ew', pady=4),
    'dept_label':           dict(row=row_int+8, column=0, sticky='e', padx=4),
    'dept_entry':           dict(row=row_int+8, column=1, columnspan=2, sticky='ew', pady=4),
    'role_label':           dict(row=row_int+9, column=0, sticky='e', padx=4),
    'role_entry':           dict(row=row_int+9, column=1, columnspan=2, sticky='ew', pady=4),
    'buttons_frame':        dict(row=row_int+10, column=0, columnspan=3, sticky='ew', pady=10),
}

"""
# --- setup container frame with padding ---
container = tk.Frame(root, padx=15, pady=15)
container.grid(row=0, column=0, sticky="nsew")

# allow container→col1 to expand
container.grid_columnconfigure(0, weight=1)
container.grid_columnconfigure(1, weight=0)
container.grid_columnconfigure(2, weight=1)
"""
# instead of excel_frame = tk.Frame(root,…)
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

# make root stretch to fill
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# create three pages
excel_frame  = tk.Frame(notebook, padx=15, pady=15)
import_frame = tk.Frame(notebook, padx=15, pady=15)
upload_elentra_link_frame = tk.Frame(notebook, padx=15, pady=15)
notebook.add(excel_frame, text="Excel")
notebook.add(import_frame, text="Import")
notebook.add(upload_elentra_link_frame, text="Upload Elentra Link")

###~~~~ EXCEL ~~~~###
# Widgets, using grid_opts:
tk.Label(excel_frame, text="LAMS User Import Excel", font=("Helvetic",14,"bold")).grid(**grid_opts['title_label'])
tk.Label(excel_frame, text="Build an Excel file for LAMS user import that lets you choose between Student and Staff lists.").grid(**grid_opts['instruction_label'])

# Mode toggle
tk.Radiobutton(excel_frame, text="Staff List", variable=mode_var, value='staff', command=switch_mode).grid(**grid_opts['mode_staff_rb'])
tk.Radiobutton(excel_frame, text="Student List", variable=mode_var, value='student', command=switch_mode).grid(**grid_opts['mode_student_rb'])

# Save folder chooser row
tk.Label(excel_frame, text="Save Folder:").grid(**grid_opts['save_label'])
tk.Entry(excel_frame, textvariable=save_dir_var).grid(**grid_opts['save_entry'])
tk.Button(excel_frame, text="Browse…", command=select_folder).grid(**grid_opts['browse_btn'])

# Header display
tk.Label(excel_frame, text="Header:").grid(**grid_opts['header_text_label'])
tk.Label(excel_frame, textvariable=header_var, fg='dark gray').grid(**grid_opts['header_label'])

# Emails input
tk.Label(excel_frame, text="Emails:").grid(**grid_opts['emails_label'])
email_text = tk.Text(excel_frame, width=1, height=8)
email_text.grid(**grid_opts['emails_text'])
email_text.insert('1.0', "user1@email.com\nuser2@email.com\nuser3@email.com\n")

# Course ID input
tk.Label(excel_frame, text="Course ID:").grid(**grid_opts['courseid_label'])
course_id_text = tk.Text(excel_frame, width=1, height=8)
course_id_text.grid(**grid_opts['courseid_text'])
course_id_text.insert('1.0', "580")

# Course Name (students only)
tk.Label(excel_frame, text="Course Name:").grid(**grid_opts['coursename_label'])
course_name_entry = tk.Entry(excel_frame, width=61)
course_name_entry.grid(**grid_opts['coursename_entry'])
course_name_entry.insert(0, "Test_Course_Name")

# Department (staff only)
tk.Label(excel_frame, text="Department:").grid(**grid_opts['dept_label'])
dept_entry = tk.Entry(excel_frame, width=61)
dept_entry.grid(**grid_opts['dept_entry'])
dept_entry.insert(0, "Test_Department")

# Role (editable)
tk.Label(excel_frame, text="Role:").grid(**grid_opts['role_label'])
role_entry = tk.Entry(excel_frame, width=1)
role_entry.grid(**grid_opts['role_entry'])
role_entry.insert(0, 'Learner')

# Buttons Frame
btn_frame = tk.Frame(excel_frame)
btn_frame.grid(**grid_opts['buttons_frame'])

# Give its columns 0 and 3 all the extra space
btn_frame.grid_columnconfigure(0, weight=1)
btn_frame.grid_columnconfigure(3, weight=1)
# do not use expand example: 
# tk.Button(btn_frame, text="Run",   width=10, command=run).pack(padx=10, pady=5, expand=True)
# tk.Button(btn_frame, text="Close", width=10, command=root.destroy).pack(padx=10, pady=5, expand=True)

# Create and grid the two buttons in the middle columns 1 & 2
run_btn = tk.Button(btn_frame, text="Run",   width=10, command=run)
run_btn.grid(row=0, column=1, padx=5)
close_btn = tk.Button(btn_frame, text="Close", width=10, command=root.destroy)
close_btn.grid(row=0, column=2, padx=5)

###~~~~ end of EXCEL ~~~~###

# --- Import tab widgets ---
tk.Label(import_frame, text="Import all .xls files from folder", font=("Helvetica",14,"bold")).grid(row=0, column=0, columnspan=3, pady=(0,8), sticky="w")

# folder to import from
tk.Label(import_frame, text="Folder:").grid(row=1, column=0, sticky='e', padx=4)
import_dir_var = tk.StringVar(value=save_dir_var.get())
tk.Entry(import_frame, textvariable=import_dir_var, width=50).grid(row=1, column=1, sticky='ew', pady=4)
tk.Button(import_frame, text="Browse…", 
          command=lambda: import_dir_var.set(filedialog.askdirectory(initialdir=import_dir_var.get())))\
  .grid(row=1, column=2, padx=4)

# scrolled text for logs
tk.Label(import_frame, text="Logs:").grid(row=2, column=0, sticky='nw', padx=4, pady=4)
log_widget = ScrolledText(import_frame, width=60, height=15, state='disabled')
log_widget.grid(row=2, column=1, columnspan=2, sticky='nsew', pady=4)

# start import button
def import_all():
    folder = import_dir_var.get().strip()
    if not os.path.isdir(folder):
        return messagebox.showerror("Error", "Please select a valid folder to import from.")
    log_widget.config(state='normal')
    log_widget.delete('1.0','end')
    for fn in os.listdir(folder):
        if fn.lower().endswith('.xls'):
            full = os.path.join(folder, fn)
            log_widget.insert('end', f"Uploading {fn}…\n")
            log_widget.see('end')
            root.update_idletasks()

            # --- placeholder for your Selenium upload code ---
            # success = your_selenium_upload_function(full)

            if success:
                log_widget.insert('end', f"✅ {fn} uploaded\n\n")
            else:
                log_widget.insert('end', f"❌ {fn} FAILED\n\n")
            log_widget.see('end')
            root.update_idletasks()
    log_widget.insert('end', "All done!\n")
    log_widget.config(state='disabled')

tk.Button(import_frame, text="Start Import", command=import_all).grid(row=3, column=1, pady=(10,0))

###

# Configure columns and window sizing
# root.grid_columnconfigure(0, weight=1)
# root.grid_rowconfigure(0, weight=1)
import_frame.grid_columnconfigure(1, weight=1)
import_frame.grid_rowconfigure(2, weight=1)
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
root.resizable(False, False)

# Initialize mode and start GUI
switch_mode()
root.mainloop()