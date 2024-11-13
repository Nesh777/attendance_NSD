import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect('NSD_attendance_system.db')  # Replace with your database file name

# Query to get students data
students_query = "SELECT * FROM students"
students_df = pd.read_sql_query(students_query, conn)

# Query to get courses data
courses_query = "SELECT * FROM courses"
courses_df = pd.read_sql_query(courses_query, conn)

# Write the data to an Excel file with multiple sheets
with pd.ExcelWriter('student_and_course.xlsx', engine='openpyxl') as writer:
    students_df.to_excel(writer, sheet_name='Students', index=False)
    courses_df.to_excel(writer, sheet_name='Courses', index=False)

# Close the connection
conn.close()


