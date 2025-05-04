import datetime
import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np
from supabase import create_client, Client

# Supabase credentials
url = "https://rahngoowmsqgkozdomhx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJhaG5nb293bXNxZ2tvemRvbWh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQzOTU0MTgsImV4cCI6MjA1OTk3MTQxOH0.3gD4NKLSz2HMckdhO045IVHDOUR4edqV9TNeTwHdRgA"
bucket_name = "schoolattendance"
supabase: Client = create_client(url, key)

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background and mode images
imgBackground = cv2.imread("Resources/background.png")
folderModePath = 'Resources/Modes'
imgModeList = [cv2.imread(os.path.join(folderModePath, f)) for f in os.listdir(folderModePath)]

# Load encodings
print("Loading Encode File ...")
with open("EncodeFile.p", 'rb') as file:
    encodeListKnown, studentIds = pickle.load(file)
print("Encode File Loaded.")

# Variables
modeType = 0
counter = 0
id = -1
imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)
studentInfo = {}

while True:
    success, img = cap.read()
    if not success:
        print("Camera read failed.")
        break

    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = [v * 4 for v in faceLoc]
                bbox = (x1 + 55, y1 + 162, x2 - x1, y2 - y1)
                cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:
                if counter == 1:
                    studentInfo = supabase.table("attendance").select("*").eq("id", str(id)).single().execute().data
                    print("Student Info:", studentInfo)

                    file_path = f"{id}.png"
                    # Inside main loop, around line 76–95
                    try:
                        response = supabase.storage.from_(bucket_name).download(file_path)
                        if hasattr(response, "content") and response.content:
                            array = np.frombuffer(response.content, np.uint8)
                            imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                            if imgStudent is None:
                                raise ValueError("cv2.imdecode returned None")
                        else:
                            raise ValueError(f"No content found for file: {file_path}")

                        # Update attendance
                        try:
                            datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                              "%Y-%m-%d %H:%M:%S")
                            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                            print(secondsElapsed)
                            if secondsElapsed >30:
                                new_total = studentInfo['total_attendance'] + 1
                                supabase.table("attendance").update({"total_attendance": new_total}).filter("id", "eq",
                                                                                                            id).execute()
                                # Update the last_attendance_time column for the given student ID
                                supabase.table("attendance").update({
                                    "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }).eq("id", id).execute()
                                studentInfo["total_attendance"] = new_total
                                from datetime import datetime

                            else:
                                modeType = 3
                                counter = 0
                                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                            if modeType != 3:
                                # ✅ Now we're outside the try-except block, safe to use if
                                if 10 < counter < 20:
                                    modeType = 2

                                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                                if counter <= 10:
                                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                    cv2.putText(imgBackground, str(id), (1006, 493),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)

                                    (text_width, _), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1,
                                                                         1)
                                    text_x = 808 + (414 - text_width) // 2
                                    cv2.putText(imgBackground, studentInfo['name'], (text_x, 445),
                                                cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)

                                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                            if studentInfo:
                                cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                cv2.putText(imgBackground, str(id), (1006, 493),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                                cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)
                                cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 2)

                                (text_width, _), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                                text_x = 808 + (414 - text_width) // 2
                                cv2.putText(imgBackground, studentInfo['name'], (text_x, 445),
                                            cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)

                                imgBackground[175:175 + 216, 909:909 + 216] = imgStudent


                        except Exception as e:
                            print(f"Failed to update attendance: {e}")

                    except Exception as e:
                        print(f"Image load error for {file_path}: {e}")
                        imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)



                    counter += 1

                    if counter>=20:
                        counter = 0
                        modeType = 0
                        studentInfo = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0


    cv2.imshow("Face Attendance", imgBackground)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break