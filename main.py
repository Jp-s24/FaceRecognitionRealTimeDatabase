import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np

cap = cv2.VideoCapture(0)  # Try 0 instead of 1 if 1 is not working
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")

# Importing the mode images into a list

folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))

# Load the encoding file

print("Loading Encode File ...")

file = open("EncodeFile.p", 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode File Loaded ...")


while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480, 55:55+640] = img
    imgBackground[44:44+633, 808:808+414] = imgModeList[3]

    for encodeFace , faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches", matches)
        # print("faceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        print("Match Index", matchIndex)

        if matches[matchIndex]:
            # print("Known Face Detected")
            # print(studentIds[matchIndex])
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4 ,y2 * 4 , x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            cvzone.cornerRect(imgBackground, bbox, rt=0)










    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

#encoding generator

