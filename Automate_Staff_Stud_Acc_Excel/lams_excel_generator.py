#!/usr/local/bin/python3

"""
lams_excel_generator.py

A simple Tkinter GUI to generate LAMS Excel files for students or staff.

Usage:
    pip3 install pandas xlwt
    python3 lams_excel_generator.py
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

# --- Constants ---
STUDENT_HEADERS = ["login", "organisation", "roles"]
STAFF_HEADERS   = ["login", "organisation", "roles", "add to lessons"]

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

    if not folder or not os.path.isdir(folder):
        return messagebox.showerror("Error", "Please select a valid Save Folder.")

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
        course_name_entry.delete(0, 'end')
        course_name_entry.config(state='disabled')
        dept_entry.config(state='normal')
        role_entry.delete(0, 'end')
        role_entry.insert(0, 'Monitor')

# --- GUI Setup ---
root = tk.Tk()
root.title("LAMS Annual Prep Staff Stud Excel Generator")

mode_var    = tk.StringVar(value='staff')
header_var  = tk.StringVar()
save_dir_var = tk.StringVar(value=os.getcwd())

# Instruction label
tk.Label(root, text="Choose student or staff list to import users into LAMS").grid(
    row=0, column=0, columnspan=3, padx=10, pady=(10,4), sticky='w')

# Mode toggle
tk.Radiobutton(root, text="Student List", variable=mode_var, value='student', command=switch_mode).grid(row=1, column=1, padx=8, pady=4, sticky='w')
tk.Radiobutton(root, text="Staff List",   variable=mode_var, value='staff',   command=switch_mode).grid(row=1, column=0, padx=8, pady=4, sticky='w')

# Save folder chooser row
tk.Label(root, text="Save Folder:").grid(row=2, column=0, sticky='e', padx=4)
save_entry = tk.Entry(root, textvariable=save_dir_var, width=50)
save_entry.grid(row=2, column=1, sticky='w', pady=4)
tk.Button(root, text="Browse…", command=select_folder).grid(row=2, column=2, padx=4)

# Header display
tk.Label(root, text="Header:").grid(row=3, column=0, sticky='e', padx=4)
header_label = tk.Label(root, textvariable=header_var, fg='blue')
header_label.grid(row=3, column=1, columnspan=2, sticky='w')

# Emails input
tk.Label(root, text="Emails:").grid(row=4, column=0, sticky='ne', padx=4, pady=4)
email_text = tk.Text(root, width=60, height=8)
email_text.grid(row=4, column=1, columnspan=2, sticky='ew', pady=4)
email_text.insert('1.0', "user1@email.com\nuser2@email.com\nuser3@email.com\n")

# Course ID input
tk.Label(root, text="Course ID:").grid(row=5, column=0, sticky='ne', padx=4, pady=4)
course_id_text = tk.Text(root, width=60, height=8)
course_id_text.grid(row=5, column=1, columnspan=2, sticky='ew', pady=4)
course_id_text.insert('1.0', "580")

# Course Name (students only)
tk.Label(root, text="Course Name:").grid(row=6, column=0, sticky='e', padx=4)
course_name_entry = tk.Entry(root, width=60)
course_name_entry.grid(row=6, column=1, columnspan=2, sticky='w', pady=4)
course_name_entry.insert(0, "Test_Course_Name")

# Department (staff only)
tk.Label(root, text="Department:").grid(row=7, column=0, sticky='e', padx=4)
dept_entry = tk.Entry(root, width=60)
dept_entry.grid(row=7, column=1, columnspan=2, sticky='w', pady=4)
dept_entry.insert(0, "Test_Department")

# Role (editable)
tk.Label(root, text="Role:").grid(row=8, column=0, sticky='e', padx=4)
role_entry = tk.Entry(root, width=60)
role_entry.grid(row=8, column=1, columnspan=2, sticky='w', pady=4)
role_entry.insert(0, 'Learner')

# Buttons Frame
btn_frame = tk.Frame(root)
btn_frame.grid(row=9, column=1, columnspan=2, pady=10)
run_btn = tk.Button(btn_frame, text="Run", width=10, command=run)
run_btn.pack(side='left', padx=5)
close_btn = tk.Button(btn_frame, text="Close", width=10, command=root.destroy)
close_btn.pack(side='left')

# Configure columns and window sizing
root.grid_columnconfigure(1, weight=1)
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
root.resizable(False, False)

# Initialize mode and start GUI
switch_mode()
root.mainloop()