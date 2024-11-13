import sqlite3
import hashlib
from datetime import datetime
from tkinter import *
from tkinter import messagebox
import tkinter as tk



# Database setup function
def setup_database():
    conn = sqlite3.connect('NSD_attendance_system.db')
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    username TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
                    course_code TEXT PRIMARY KEY,
                    course_name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    student_id INTEGER,
                    course_code TEXT,
                    date TEXT,
                    status TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(course_code) REFERENCES courses(course_code))''')
    
    # Insert default instructor user (username: instructor, password: instruct123)
    instructor_password = hashlib.sha256("instruct123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", ("instructor", instructor_password, "instructor"))
    
    conn.commit()
    conn.close()

# Helper function for hashing passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to verify login credentials
def verify_login(username, password):
    conn = sqlite3.connect('NSD_attendance_system.db')
    c = conn.cursor()
    hashed_password = hash_password(password)
    c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

# Add a new student with a password as their first name + "123"
def add_student(name, username):
    conn = sqlite3.connect('NSD_attendance_system.db')
    c = conn.cursor()
    
    # Set the password to be the student's name + "123"
    password = hash_password(name + "123")
    
    # Insert student record in the students table and user login in users table
    c.execute("INSERT INTO students (name, username) VALUES (?, ?)", (name, username))
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, "student"))
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Student '{name}' added with username '{username}' and password '{name}123'")

# Add a new course
def add_course(course_code, course_name):
    conn = sqlite3.connect('NSD_attendance_system.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO courses (course_code, course_name) VALUES (?, ?)", (course_code, course_name))
    conn.commit()
    conn.close()

# Mark attendance using student's name instead of ID
def mark_attendance(student_name, course_code, status):
    conn = sqlite3.connect('NSD_attendance_system.db')
    c = conn.cursor()
    
    # Get student ID based on the name
    c.execute("SELECT id FROM students WHERE name = ?", (student_name,))
    student = c.fetchone()

    if not student:
        messagebox.showerror("Error", "Student not found.")
        return
    
    student_id = student[0]
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Insert attendance record using student ID
    c.execute("INSERT INTO attendance (student_id, course_code, date, status) VALUES (?, ?, ?, ?)", 
              (student_id, course_code, date, status))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Attendance for student '{student_name}' marked as '{status}' for course '{course_code}' on '{date}'")

# View attendance for a student by their name
def view_student_attendance(username):
    conn = sqlite3.connect('NSD_attendance_system.db')
    c = conn.cursor()
    c.execute("SELECT id, name FROM students WHERE username = ?", (username,))
    student = c.fetchone()
    
    if not student:
        messagebox.showerror("Error", "Student not found.")
        return
    
    student_id, student_name = student
    c.execute('''SELECT c.course_code, c.course_name, a.date, a.status
                 FROM attendance a
                 JOIN courses c ON a.course_code = c.course_code
                 WHERE a.student_id = ?
                 ORDER BY a.date DESC''', (student_id,))
    
    records = c.fetchall()
    conn.close()
    
    if records:
        records_text = f"\nAttendance Records for {student_name}:\n"
        for course_code, course_name, date, status in records:
            records_text += f"{course_code} - {course_name} | Date: {date} | Status: {status}\n"
        messagebox.showinfo("Attendance Records", records_text)
    else:
        messagebox.showinfo("Attendance", "No attendance records found.")

# Instructor Menu GUI
def instructor_menu(root):
    def add_student_gui():
        def submit_student():
            name = student_name_entry.get()
            username = student_username_entry.get()
            if name and username:
                add_student(name, username)
            else:
                messagebox.showwarning("Input Error", "Please fill all fields.")
        
        add_student_window = Toplevel(root)
        add_student_window.title("Add Student")
        
        Label(add_student_window,font=(15), text="Enter Student Name:").pack()
        student_name_entry = Entry(add_student_window)
        student_name_entry.pack()
        
        Label(add_student_window,font=(15), text="Enter Student Username:").pack()
        student_username_entry = Entry(add_student_window)
        student_username_entry.pack()
        
        Button(add_student_window, text="Submit",bg='red',font=(20), command=submit_student).pack()

    def add_course_gui():
        def submit_course():
            course_code = course_code_entry.get()
            course_name = course_name_entry.get()
            if course_code and course_name:
                add_course(course_code, course_name)
            else:
                messagebox.showwarning("Input Error", "Please fill all fields.")
        
        add_course_window = Toplevel(root)
        add_course_window.title("Add Course")
        
        Label(add_course_window,font=(15), text="Enter Course Code:").pack()
        course_code_entry = Entry(add_course_window)
        course_code_entry.pack()
        
        Label(add_course_window,font=(15), text="Enter Course Name:").pack()
        course_name_entry = Entry(add_course_window)
        course_name_entry.pack()
        
        Button(add_course_window, text="Submit",bg='red',font=(20), command=submit_course).pack()

    def mark_attendance_gui():
        def submit_attendance():
            student_name = student_name_entry.get()
            course_code = course_code_entry.get()
            status = status_var.get()
            if student_name and course_code and status:
                mark_attendance(student_name, course_code, status)
            else:
                messagebox.showwarning("Input Error", "Please fill all fields.")
        
        mark_attendance_window = Toplevel(root)
        mark_attendance_window.title("Mark Attendance")
        
        Label(mark_attendance_window,font=(15), text="Enter Student Name:").pack()
        student_name_entry = Entry(mark_attendance_window)
        student_name_entry.pack()
        
        Label(mark_attendance_window,font=(15), text="Enter Course Code:").pack()
        course_code_entry = Entry(mark_attendance_window)
        course_code_entry.pack()
        
        Label(mark_attendance_window,font=(15), text="Enter Attendance Status (Present/Absent):").pack()
        status_var = StringVar(value="Present")
        OptionMenu(mark_attendance_window, status_var, "Present", "Absent").pack()
        
        Button(mark_attendance_window, text="Submit",bg='red',font=(20), command=submit_attendance).pack()

    def logout():
        root.quit()

    # Main instructor menu
    instructor_frame = Frame(root)
    instructor_frame.pack(pady=20)

    Button(instructor_frame, text="Add Student",bg='lightgreen', command=add_student_gui).pack(pady=5)
    Button(instructor_frame, text="Add Course",bg='lightgreen', command=add_course_gui).pack(pady=5)
    Button(instructor_frame, text="Mark Attendance",bg='lightgreen', command=mark_attendance_gui).pack(pady=5)
    Button(instructor_frame, text="Logout",bg='lightgreen', command=logout).pack(pady=5)

# Student Menu GUI
def student_menu(username, root):
    def view_attendance_gui():
        view_student_attendance(username)

    def logout():
        root.quit()

    # Main student menu
    student_frame = Frame(root)
    student_frame.pack(pady=20)

    Button(student_frame, text="View Attendance",bg='blue', command=view_attendance_gui).pack(pady=10)
    Button(student_frame, text="Logout",bg='blue', command=logout).pack(pady=10)

# Main login GUI
def login_gui():
    def login():
        username = username_entry.get()
        password = password_entry.get()
        role = verify_login(username, password)
        
        if role == "instructor":
            print("Login successful. Welcome, Instructor!")
            instructor_menu(root)
        elif role == "student":
            print(f"Login successful. Welcome, Student {username}!")
            student_menu(username, root)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    root = Tk()
    root.title("Attendance System Login")
    root.configure(bg = "lightgreen")
    root.geometry("800x600")

    Label(root,text="Username").pack(pady=5)
    username_entry = Entry(root)
    username_entry.pack(pady=5)

    Label(root, text="Password").pack(pady=5)
    password_entry = Entry(root, show="*")
    password_entry.pack(pady=5)

    Button(root, text="Login",bg='blue',font=(20), command=login).pack(pady=10)

    root.mainloop()
    

if __name__ == "__main__":
    setup_database()
    login_gui()
