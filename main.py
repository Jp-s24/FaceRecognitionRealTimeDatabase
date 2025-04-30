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

# Load background image
imgBackground = cv2.imread("Resources/background.png")

# Load all mode images
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load encoding file
print("Loading Encode File ...")
with open("EncodeFile.p", 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded.")

# Variables
modeType = 0
counter = 0
id = -1
imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame from webcam.")
        break

    # Resize and convert for face recognition
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Overlay camera and mode images
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            x1b, y1b = x1 + 55, y1 + 162
            x2b, y2b = x2 + 55, y2 + 162
            w, h = x2b - x1b, y2b - y1b

            bbox = (x1b, y1b, w, h)
            cvzone.cornerRect(imgBackground, bbox, rt=0)

            id = studentIds[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1

        if counter != 0:
            if counter == 1:
                studentInfoResponse = supabase.table("attendance").select("*").eq("id", str(id)).single().execute()
                studentInfo = studentInfoResponse.data
                print(studentInfo)

                file_path = f"{id}.png"
                try:
                    imgStudent = supabase.storage.from_(bucket_name).download(file_path)
                    if imgStudent:
                        # If download succeeds, the response will be in bytes
                        image_bytes = imgStudent
                        array = np.frombuffer(image_bytes, np.uint8)
                        imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    else:
                        print(f"Failed to download student image: Image not found for {file_path}")
                        imgStudent = None
                except Exception as e:
                    print(f"An error occurred while downloading the file: {e}")
                    imgStudent = None

                if imgStudent is None:
                    print("No image was loaded, check if the file exists in Supabase.")

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

                (w, _), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w) // 2

                cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)

                imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

            counter += 1

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
