import datetime

from supabase import create_client, Client

# Replace with your actual details
url = "https://rahngoowmsqgkozdomhx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhaG5nb293bXNxZ2tvemRvbWh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzOTU0MTgsImV4cCI6MjA1OTk3MTQxOH0.3gD4NKLSz2HMckdhO045IVHDOUR4edqV9TNeTwHdRgA"

supabase: Client = create_client(url, key)

# Example new student attendance record
new_student1 = {
    "name": "Murtaza Hassan",
    "last_attendance_time": "2022-12-11 00:54:34",
    "major": "Robotics",
    "starting_year": 2017,
    "total_attendance": 7,
    "standing": "G",
    "year": 4
},

new_student2 = {
    "name": "Emily Blunt",
    "last_attendance_time": "2022-12-11 00:54:34",
    "major": "Economics",
    "starting_year": 2018,
    "total_attendance": 12,
    "standing": "B",
    "year": 2
},

new_student3 = {
    "name": "Elon Musk",
    "last_attendance_time": "2022-12-11 00:54:34",
    "major": "Physics",
    "starting_year": 2020,
    "total_attendance": 7,
    "standing": "G",
    "year": 2
}



# Insert into Supabase
response = supabase.table('attendance').insert(new_student1).execute()
response = supabase.table('attendance').insert(new_student2).execute()
response = supabase.table('attendance').insert(new_student3).execute()



print("Inserted data:", response.data)
