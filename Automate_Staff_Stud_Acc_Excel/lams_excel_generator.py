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
from tkinter import messagebox
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


def save_xls(filename, headers, rows):
    """
    Write rows (list of lists) with headers (list) to an XLS file via xlwt.
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
    wb.save(filename)
    return filename

# --- Build Functions ---
def build_student_file(course_name, course_id, emails):
    """
    Generate a single student-list .xls file.
    """
    today = datetime.now().strftime("%d%m%y")
    rows = []
    for email in emails:
        rows.append([email, course_id, "Learner"] )
    filename = f"{course_name}_CID{course_id}_{today}.xls"
    return save_xls(filename, STUDENT_HEADERS, rows)


def build_staff_files(department, course_id, emails):
    """
    Generate one staff-list .xls file per email.
    """
    files = []
    for email in emails:
        rows = [[email, course_id, "Monitor", "Yes"]]
        filename = f"{department}_{email}.xls"
        files.append(save_xls(filename, STAFF_HEADERS, rows))
    return files

# --- GUI Setup ---
root = tk.Tk()
root.title("LAMS Annual Prep Staff Stud Excel Generator")

mode_var = tk.StringVar(value='student')
header_var = tk.StringVar()

# Mode toggle
tk.Radiobutton(root, text="Student List", variable=mode_var, value='student', command=lambda: switch_mode()).grid(row=0, column=0, padx=8, pady=4, sticky='w')
tk.Radiobutton(root, text="Staff List",   variable=mode_var, value='staff',   command=lambda: switch_mode()).grid(row=0, column=1, padx=8, pady=4, sticky='w')

# Header display
tk.Label(root, text="Header:").grid(row=1, column=0, sticky='e', padx=4)
header_label = tk.Label(root, textvariable=header_var, fg='blue')
header_label.grid(row=1, column=1, columnspan=2, sticky='w')

# Emails input
tk.Label(root, text="Emails:").grid(row=2, column=0, sticky='ne', padx=4, pady=4)
email_text = tk.Text(root, width=60, height=8)
email_text.grid(row=2, column=1, columnspan=2, sticky='ew', pady=4)
email_text.insert('1.0', "Enter emails, one per line or comma-separated")

# Course ID input
tk.Label(root, text="Course ID:").grid(row=3, column=0, sticky='ne', padx=4, pady=4)
course_id_text = tk.Text(root, width=60, height=8)
course_id_text.grid(row=3, column=1, columnspan=2, sticky='ew', pady=4)
course_id_text.insert('1.0', "Enter Course ID")

# Course Name (students only)
tk.Label(root, text="Course Name:").grid(row=4, column=0, sticky='e', padx=4)
course_name_entry = tk.Entry(root, width=60)
course_name_entry.grid(row=4, column=1, columnspan=2, sticky='w', pady=4)

# Department (staff only)
tk.Label(root, text="Department:").grid(row=5, column=0, sticky='e', padx=4)
dept_entry = tk.Entry(root, width=60)
dept_entry.grid(row=5, column=1, columnspan=2, sticky='w', pady=4)

# Role (editable)
tk.Label(root, text="Role:").grid(row=6, column=0, sticky='e', padx=4)
role_entry = tk.Entry(root, width=60)
role_entry.grid(row=6, column=1, columnspan=2, sticky='w', pady=4)
role_entry.insert(0, 'Learner')

# Buttons: Run and Close
run_btn = tk.Button(root, text="Run", width=10, command=lambda: run())
run_btn.grid(row=7, column=1, pady=10, sticky='e')
close_btn = tk.Button(root, text="Close", width=10, command=root.destroy)
close_btn.grid(row=7, column=2, pady=10, sticky='w')

# --- Callbacks ---
def run():
    mode = mode_var.get()
    emails = parse_emails(email_text.get('1.0', 'end'))
    cid = course_id_text.get('1.0', 'end').strip()

    if mode == 'student':
        name = course_name_entry.get().strip()
        if not (emails and cid and name):
            return messagebox.showerror("Error",
                "Please fill Course Name, Course ID, and Emails.")
        filename = build_student_file(name, cid, emails)
        messagebox.showinfo("Success", f"Generated: {filename}")

    else:  # staff mode
        dept = dept_entry.get().strip()
        role = role_entry.get().strip()
        if not (emails and cid and dept and role):
            return messagebox.showerror("Error",
                "Please fill Department, Course ID, Role, and Emails.")
        files = build_staff_files(dept, cid, emails)
        messagebox.showinfo("Success",
            f"Generated {len(files)} files:\n" + "\n".join(files))


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

# Initialize mode and start GUI
switch_mode()
root.mainloop()