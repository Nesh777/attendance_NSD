import sqlite3
import pandas as pd

conn = sqlite3.connect('NSD_attendance_system.db')  

students_query = "SELECT * FROM students"
students_df = pd.read_sql_query(students_query, conn)

courses_query = "SELECT * FROM courses"
courses_df = pd.read_sql_query(courses_query, conn)

with pd.ExcelWriter('student_and_course.xlsx', engine='openpyxl') as writer:
    students_df.to_excel(writer, sheet_name='Students', index=False)
    courses_df.to_excel(writer, sheet_name='Courses', index=False)

conn.close()


