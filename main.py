import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)  # Use 0 for the default camera
cap.set(3, 640)
cap.set(4, 480)

# Load background image
imgBackground = cv2.imread("Resources/background.png")

# Load all mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load encoding file
print("Loading Encode File ...")
with open("EncodeFile.p", 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded.")

# Main loop
while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame from webcam.")
        break

    # Resize and convert image to RGB for face recognition
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detect faces and encode them
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Overlay webcam and mode image on the background
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[3]

    # Process each detected face
    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)
        print("Match Index:", matchIndex)

        if matches[matchIndex]:
            # Get face location and scale back up
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            # Offset for background image placement
            x1b, y1b = x1 + 55, y1 + 162
            x2b, y2b = x2 + 55, y2 + 162

            w, h = x2b - x1b, y2b - y1b
            bbox = (x1b, y1b, w, h)

            # Draw rectangle using cvzone
            cvzone.cornerRect(imgBackground, bbox, rt=0)

    # Show the final frame
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
